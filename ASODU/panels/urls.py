from django.urls import path

from . import views

app_name = 'panels'

urlpatterns = [
    path(
        '',
        views.index, name='index',
    ),
    path(
        'projects/<int:project_id>/',
        views.project_detail,
        name='project_detail',
    ),
    path(
        'panels/<int:panel_id>/',
        views.panel_detail,
        name='panel_detail',
    ),
    path(
        'projects/<int:project_id>/create/',
        views.panel_create,
        name='panel_create',
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
        'panels/<int:panel_id>/delete/',
        views.panel_delete,
        name='panel_delete',
    ),
    path(
        'panels/<int:panel_id>/edit/',
        views.panel_edit,
        name='panel_edit',
    ),
]
