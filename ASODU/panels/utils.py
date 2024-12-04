from django.db.models import Prefetch, Q
from django.shortcuts import get_list_or_404, get_object_or_404

from panels.models import EquipmentPanelAmount, Panel, Project


def get_accessible_panel(
        request, id: int, published: bool = False, project_id: int = None
):
    query = Q(
        project__in=request.user.co_projects.all()
    ) | Q(project__author=request.user)
    if published:
        query |= Q(project__is_published=True)

    queryset = Panel.objects.prefetch_related(
        Prefetch(
            'amounts',
            queryset=EquipmentPanelAmount.objects.select_related(
                'equipment', 'equipment__vendor', 'equipment__group')
        ),
        'attachments'
    ).select_related('project').order_by('name')

    if project_id is None:
        panel = get_object_or_404(queryset, query, pk=id)
        return panel
    else:
        panels = get_list_or_404(queryset, query, project__id=project_id)
        return panels


def get_accessible_project(request, id: int):
    project = get_object_or_404(
        Project.objects.select_related('author'),
        Q(is_published=True)
        | Q(id__in=request.user.co_projects.values_list('id', flat=True))
        | Q(author=request.user),
        pk=id,
    )
    return project


def amounts_by_group(panel: Panel) -> dict:
    amounts_by_group = {}
    for amount in panel.amounts.all():
        group = amount.equipment.group
        amounts_by_group[group] = amounts_by_group.get(group, [])
        amounts_by_group[group].append(amount)
    return amounts_by_group
