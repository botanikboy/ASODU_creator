from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from .models import Project, Panel
from .forms import PanelForm, ProjectForm, EquipmentFormset
from .utils import paginator_create


@login_required
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


def project_edit(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    form = ProjectForm(request.POST or None, instance=project)
    if form.is_valid():
        project = form.save(commit=False)
        project.save()
        return redirect('panels:project_detail', project.id)
    else:
        context = {
            'form': form,
            'is_edit': True,
        }
        return render(request, 'panels/create_project.html', context)


def project_delete(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if Panel.objects.filter(project=project).exists():
        return redirect('panels:project_detail', project.id)
    if project.author == request.user:
        project.delete()
    return redirect('panels:index')


# -----------------------------------------panels---------------------
def panel_detail(request, panel_id):
    panel = get_object_or_404(Panel, pk=panel_id)
    context = {
        'panel': panel
    }
    return render(request, 'panels/panel_detail.html', context)


def panel_create(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    form = PanelForm(request.POST or None)
    if request.method == 'POST':
        form.instance.project = project
    if form.is_valid():
        panel = form.save(commit=False)
        # panel.project = project уже присваивается выше в инстансе
        panel.save()
        return redirect('panels:project_detail', project.id)
    else:
        context = {
            'form': form,
            'project': project,
        }
        return render(request, 'panels/create_panel.html', context)


def panel_edit(request, panel_id):
    panel = get_object_or_404(Panel, pk=panel_id)
    form = PanelForm(request.POST or None, instance=panel)
    print(form)
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


def panel_edit_contents(request, panel_id):
    panel = get_object_or_404(Panel, pk=panel_id)
    formset = EquipmentFormset(request.POST or None, instance=panel)
    project = panel.project
    if formset.is_valid():
        for form in formset:
            if form.is_valid() and not form.empty_permitted:
                if form.cleaned_data.get('DELETE'):
                    form.instance.delete()
                else:
                    equipment = form.save(commit=False)
                    equipment.panel = panel
                    equipment.save()
        return redirect('panels:panel_detail', panel.id)
    else:
        print(formset.non_form_errors())
        context = {
            'form': formset,
            'project': project,
            'is_edit': True,
        }
        return render(request, 'panels/edit_panel.html', context)


def panel_delete(request, panel_id):
    panel = get_object_or_404(Panel, pk=panel_id)
    project = panel.project
    if project.author == request.user:
        panel.delete()
    return redirect('panels:project_detail', project.id)
