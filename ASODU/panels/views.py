import os
import shutil

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch, Q
from django.http import FileResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (AttachmentForm, CoAuthorForm, EquipmentFormset,
                    PanelCopyForm, PanelForm, ProjectForm, UlErrorList)
from .models import Attachment, EquipmentPanelAmount, Panel, Project
from .utils import excelreport, get_accessible_panel, get_accessible_project
from core.utils import paginator_create, transliterate

User = get_user_model()


@login_required
def index(request):
    projects = request.user.projects.all()
    context = {
        'page_obj': paginator_create(projects, request.GET.get('page')),
    }
    return render(request, 'panels/index.html', context)


@login_required
def project_list(request):
    projects = Project.objects.filter(
        Q(is_published=True) | Q(id__in=request.user.co_projects.values('id'))
    )
    context = {
        'page_obj': paginator_create(projects, request.GET.get('page')),
    }
    return render(request, 'panels/index.html', context)


@login_required
def template_list(request):
    return render(request, 'panels/template_list.html')


@login_required
def project_detail(request, project_id):
    project = get_accessible_project(request, project_id)
    panels = project.panels.all().prefetch_related(
        Prefetch(
            'amounts',
            queryset=EquipmentPanelAmount.objects.select_related(
                'equipment', 'equipment__vendor')
        )
    )
    context = {
        'page_obj': paginator_create(panels, request.GET.get('page')),
        'project': project
    }
    return render(request, 'panels/project_detail.html', context)


@login_required
def project_create(request):
    form = ProjectForm(request.POST or None)
    user = request.user
    if form.is_valid():
        project = form.save(commit=False)
        project.author = user
        project.save()
        return redirect('panels:project_detail', project.id)
    else:
        context = {
            'form': form,
        }
        return render(request, 'panels/create_project.html', context)


@login_required
def project_edit(request, project_id):
    project = get_object_or_404(
        Project, pk=project_id,
        author=request.user)
    form = ProjectForm(request.POST or None, instance=project)
    if form.is_valid():
        form.save()
        return redirect('panels:project_detail', project.id)
    else:
        context = {
            'form': form,
            'is_edit': True,
        }
        return render(request, 'panels/create_project.html', context)


@login_required
def project_delete(request, project_id):
    project = get_object_or_404(
        Project, pk=project_id,
        author=request.user)
    if Panel.objects.filter(project=project).exists():
        return redirect('panels:project_detail', project.id)
    project.delete()
    return redirect('panels:index')


@login_required
def panel_detail(request, panel_id):
    panel = get_accessible_panel(request, panel_id, True)
    context = {
        'panel': panel
    }
    return render(request, 'panels/panel_detail.html', context)


@login_required
def panel_create(request, project_id):
    project = get_object_or_404(
        Project,
        Q(author=request.user)
        | Q(id__in=request.user.co_projects.values_list('id', flat=True)),
        pk=project_id,
    )
    form = PanelForm(request.POST or None)
    if request.method == 'POST':
        form.instance.project = project
    if form.is_valid():
        panel = form.save(commit=False)
        panel.save()
        return redirect('panels:project_detail', project.id)
    else:
        context = {
            'form': form,
            'project': project,
        }
        return render(request, 'panels/create_panel.html', context)


@login_required
def panel_edit(request, panel_id):
    panel = get_accessible_panel(request, panel_id)
    form = PanelForm(request.POST or None, instance=panel)
    if form.is_valid():
        form.save()
        return redirect('panels:panel_detail', panel.id)
    else:
        context = {
            'form': form,
            'is_edit': True,
            'project': panel.project,
        }
        return render(request, 'panels/create_panel.html', context)


@login_required
def panel_edit_contents(request, panel_id):
    panel = get_accessible_panel(request, panel_id)
    formset = EquipmentFormset(
        request.POST or None, instance=panel, error_class=UlErrorList)
    project = panel.project
    if formset.is_valid():
        for form in formset:
            if form['equipment'].value():
                if form.cleaned_data.get('DELETE') and form.instance.pk:
                    equipment = EquipmentPanelAmount.objects.get(
                        pk=form.instance.pk)
                    equipment.delete()
                if not form.cleaned_data.get('DELETE'):
                    form.save()
        return redirect('panels:panel_detail', panel.id)
    else:
        context = {
            'equipment_formset': formset,
            'project': project,
        }
        return render(request, 'panels/edit_panel.html', context)


@login_required
def panel_delete(request, panel_id):
    panel = get_accessible_panel(request, panel_id)
    panel.delete()
    return redirect('panels:project_detail', panel.project.id)


@login_required
def panel_copy(request, panel_id):
    panel = get_accessible_panel(request, panel_id, True)
    form = PanelCopyForm(request.POST or None, instance=panel, request=request)
    form.instance.pk = None
    if form.is_valid():
        form.save()
        for item in panel.amounts.all():
            item.pk = None
            item.panel = form.instance
            item.save()
        for attachment in panel.attachments.all():
            attachment.pk = None
            attachment.panel = form.instance
            source_path = attachment.drawing.path
            new_folder = os.path.join(
                settings.MEDIA_ROOT,
                'panels/',
                f'{panel.project.pk}',
                f'{form.instance.pk}_{transliterate(form.instance.name)}'
            )
            os.makedirs(new_folder, exist_ok=True)
            new_file = os.path.join(new_folder, os.path.basename(source_path))
            shutil.copy2(source_path, new_file)
            attachment.drawing.name = os.path.relpath(
                new_file, settings.MEDIA_ROOT)
            attachment.save()
        return redirect('panels:panel_detail', panel.id)
    else:
        context = {
            'form': form,
            'is_copy': True,
            'project': panel.project,
        }
        return render(request, 'panels/create_panel.html', context)


@login_required
def boq_download(request, obj_id, model):
    if model == 'panel':
        obj = get_accessible_panel(request, obj_id, True)
        panels = [obj]
    elif model == 'project':
        obj = get_accessible_project(request, obj_id)
        panels = (
            Panel.objects.filter(project=obj)
            .order_by('name')
            .prefetch_related(
                Prefetch(
                    'amounts',
                    queryset=EquipmentPanelAmount.objects.select_related(
                        'equipment', 'equipment__vendor')
                )
            )
        )
    else:
        return HttpResponseBadRequest("Invalid model parameter")

    filename = f'{obj.name} спецификация.xlsx'
    report = excelreport(panels)
    return FileResponse(report, as_attachment=True, filename=filename)


@login_required
def file_add(request, panel_id):
    panel = get_accessible_panel(request, panel_id)
    form = AttachmentForm(request.POST or None, request.FILES or None)
    if request.method == 'POST':
        form.instance.panel = panel
    if form.is_valid():
        file = form.save(commit=False)
        file.panel = panel
        file.save()
        return redirect('panels:panel_detail', panel.id)
    else:
        context = {
            'panel': panel,
            'form': form,
        }
        return render(request, 'panels/add_file.html', context)


@login_required
def file_delete(request, attachment_id):
    attachment = get_object_or_404(
        Attachment,
        Q(panel__project__author=request.user)
        | Q(panel__project__in=request.user.co_projects.all()),
        pk=attachment_id)
    if attachment.panel.project.author == request.user:
        attachment.delete()
    return redirect('panels:panel_detail', attachment.panel.id)


@login_required
def author_add(request, project_id):
    project = get_object_or_404(
        Project,
        author=request.user,
        pk=project_id)
    form = CoAuthorForm(request.POST or None, project=project)
    users = User.objects.all()
    if form.is_valid():
        form.save()
        return redirect('panels:project_detail', project.id)
    else:
        context = {
            'project': project,
            'form': form,
            'users': users
        }
        return render(request, 'panels/coauthor_form.html', context)
