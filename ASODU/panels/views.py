import io

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.db.models import Prefetch, Q
from django.http import (FileResponse, Http404, HttpResponseBadRequest,
                         JsonResponse)
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (AttachmentForm, CoAuthorForm, PanelCopyForm, PanelForm,
                    ProjectForm)
from .models import Attachment, EquipmentPanelAmount, Panel, Project
from .services import (build_panel_group_formsets, copy_panel,
                       enqueue_excel_report, save_panel_group_formsets)
from .utils import (amounts_by_group, get_accessible_panel,
                    get_accessible_project)
from core.utils import paginator_create

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
        'panel': panel,
        'amounts_by_group': amounts_by_group(panel),
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
    group_formsets = build_panel_group_formsets(request, panel)

    if request.method == 'POST':
        all_valid = all(
            formset['formset'].is_valid() for formset in group_formsets
        )

        if all_valid:
            save_panel_group_formsets(group_formsets)
            return redirect('panels:panel_edit_contents', panel.id)

    context = {
        'group_formsets': group_formsets,
        'panel': panel
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
    form = PanelCopyForm(
        request.POST or None,
        request=request,
        initial={
            'name': panel.name,
            'description': panel.description,
            'project': panel.project_id,
        }
    )
    if form.is_valid():
        copied_panel = copy_panel(
            panel,
            project=form.cleaned_data['project'],
            name=form.cleaned_data['name'],
            description=form.cleaned_data['description'],
        )
        return redirect('panels:panel_detail', copied_panel.id)
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
        panels = [get_accessible_panel(request, obj_id, True)]
    elif model == 'project':
        project = get_accessible_project(request, obj_id)
        panels = get_accessible_panel(request, obj_id, True, project.id)
    else:
        return HttpResponseBadRequest("Invalid model parameter")

    report_key = enqueue_excel_report(
        panels=panels,
        user=request.user,
        model=model,
        obj_id=obj_id,
    )

    context = {
        'report_key': report_key
    }
    return render(request, 'panels/report_done.html', context)


@login_required
def download_report(request, report_key):
    report_data = cache.get(f"report:{report_key}")
    if not report_data:
        raise Http404(
            'Спецификация еще не собрана, обновите страницу позже. '
            'Если спецификация запрошена более 10 минут назад нужно '
            'запросить её заново.')

    buffer = io.BytesIO(report_data)
    return FileResponse(
        buffer, as_attachment=True,
        filename=f'{report_key.rsplit("-", 1)[0]}-спецификация.xlsx')


@login_required
def report_status(request, report_key):
    status = cache.get(f"report_status:{report_key}", "pending")
    print(status)
    return JsonResponse({"status": status})


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
def coauthors_set(request, project_id):
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
