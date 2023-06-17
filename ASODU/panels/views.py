from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib.auth.decorators import login_required

from .models import Project, Panel
from .forms import PanelForm, ProjectForm, EquipmentFormset
from .utils import paginator_create


# @login_required
def index(request):
    projects = request.user.projects.all()
    context = {
        'page_obj': paginator_create(projects, request.GET.get('page')),
    }
    return render(request, 'panels/index.html', context)


def project_detail(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    panels = project.panels.all()
    context = {
        'page_obj': paginator_create(panels, request.GET.get('page')),
        'project': project
    }
    return render(request, 'panels/project_detail.html', context)


def panel_detail(request, panel_id):
    panel = get_object_or_404(Panel, pk=panel_id)
    context = {
        'panel': panel
    }
    return render(request, 'panels/panel_detail.html', context)


def panel_create(request, project_id):
    form = PanelForm(request.POST or None)
    project = get_object_or_404(Project, pk=project_id)
    if form.is_valid():
        panel = form.save(commit=False)
        panel.project = project
        panel.save()
        return redirect('panels:project_detail', project.id)
    else:
        context = {
            'form': form,
            'project': project
        }
        return render(request, 'panels/create_panel.html', context)


def panel_edit(request, panel_id):
    panel = get_object_or_404(Panel, pk=panel_id)
    formset = EquipmentFormset(request.POST or None, instance=panel)
    project = panel.project
    if formset.is_valid():
        panel.save()
        return redirect('panels:panel_detail', panel.id)
    else:
        context = {
            'form': formset,
            'project': project
        }
        return render(request, 'panels/create_panel.html', context)


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


def project_delete(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if Panel.objects.filter(project=project).exists():
        return redirect('panels:project_detail', project.id)
    if project.author == request.user:
        project.delete()
    return redirect('panels:index')


def panel_delete(request, panel_id):
    panel = get_object_or_404(Panel, pk=panel_id)
    project = panel.project
    if project.author == request.user:
        panel.delete()
    return redirect('panels:project_detail', project.id)
