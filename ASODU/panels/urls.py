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
]
