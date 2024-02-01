from django.urls import path

from . import views

app_name = 'panels'

urlpatterns = [
    path(
        '',
        views.index, name='index',
    ),
    path(
        'templates/',
        views.template_list,
        name='template_list',
    ),
    path(
        'projects/',
        views.project_list,
        name='project_list',
    ),
    path(
        'projects/<int:project_id>/',
        views.project_detail,
        name='project_detail',
    ),
    path(
        'projects/<int:project_id>/edit/',
        views.project_edit,
        name='project_edit',
    ),
    path(
        'projects/create/',
        views.project_create,
        name='project_create',
    ),
    path(
        'projects/<int:project_id>/delete/',
        views.project_delete,
        name='project_delete',
    ),
    path(
        'panels/<int:panel_id>/',
        views.panel_detail,
        name='panel_detail',
    ),
    path(
        'projects/<int:project_id>/add/',
        views.panel_create,
        name='panel_create',
    ),
    path(
        'projects/<int:obj_id>/boq_download/',
        views.boq_download,
        {'model': 'project'},
        name='boq_download_project',
    ),
    path(
        'panels/<int:panel_id>/delete/',
        views.panel_delete,
        name='panel_delete',
    ),
    path(
        'panels/<int:panel_id>/edit/',
        views.panel_edit,
        name='panel_edit',
    ),
    path(
        'panels/<int:panel_id>/edit_contents/',
        views.panel_edit_contents,
        name='panel_edit_contents',
    ),
    path(
        'panels/<int:panel_id>/copy/',
        views.panel_copy,
        name='panel_copy',
    ),
    path(
        'panels/<int:obj_id>/boq_download/',
        views.boq_download,
        {'model': 'panel'},
        name='boq_download_panel',
    ),
    path(
        'panels/<int:panel_id>/file_add/',
        views.file_add,
        name='file_add',
    ),
    path(
        'panels/<int:attachment_id>/file_delete/',
        views.file_delete,
        name='file_delete',
    ),
]
