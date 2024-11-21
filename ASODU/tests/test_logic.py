from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects

from panels.models import Project


def test_author_can_create_project(author_client, project_create_form_data):
    response = author_client.post(
        reverse('panels:project_create'),
        data=project_create_form_data)
    assert response.status_code == HTTPStatus.FOUND
    assert Project.objects.count() == 1
    project = Project.objects.get()
    assertRedirects(
        response,
        reverse('panels:project_detail', args=(project.id,)))
    assert project.name == project_create_form_data['name']
    assert project.description == project_create_form_data['description']
    assert project.is_published == project_create_form_data['is_published']


@pytest.mark.parametrize(
    'param_project, expected_status',
    (
        ('project', HTTPStatus.FOUND),
        ('unpublished_project', HTTPStatus.FOUND),
        ('alien_project', HTTPStatus.NOT_FOUND),
        ('alien_unpublished_project', HTTPStatus.NOT_FOUND),
        ('alien_unpublished_coauthor_project', HTTPStatus.NOT_FOUND),
    )
)
def test_author_can_edit_only_his_project(
    request, author_client, param_project, project_edit_form_data,
    expected_status
):
    param_project = request.getfixturevalue(param_project)
    response = author_client.post(
        reverse('panels:project_edit', args=(param_project.id,)),
        data=project_edit_form_data)
    assert response.status_code == expected_status

    if expected_status == HTTPStatus.FOUND:
        assertRedirects(
            response,
            reverse('panels:project_detail', args=(param_project.id,))
        )
        param_project.refresh_from_db()
        assert (
            param_project.is_published
            == project_edit_form_data['is_published'])
        assert (param_project.name == project_edit_form_data['name'])
        assert (
            param_project.description
            == project_edit_form_data['description'])


@pytest.mark.parametrize(
    'param_project, expected_status',
    (
        ('project', HTTPStatus.FOUND),
        ('alien_project', HTTPStatus.NOT_FOUND),
        ('alien_unpublished_coauthor_project', HTTPStatus.NOT_FOUND),
    )
)
def test_only_author_can_delete_empty_project(
    request, author_client, param_project, expected_status
):
    param_project = request.getfixturevalue(param_project)
    response = author_client.delete(
        reverse('panels:project_delete', args=(param_project.id,)))
    assert response.status_code == expected_status
    if expected_status == HTTPStatus.FOUND:
        assertRedirects(response, reverse('panels:index'))
        assert Project.objects.count() == 0
    else:
        assert Project.objects.count() == 1


def test_author_cant_delete_nonempty_project(author_client, project, panel):
    response = author_client.delete(
        reverse('panels:project_delete', args=(project.id,)))
    assert response.status_code == HTTPStatus.FOUND
    assertRedirects(
        response, reverse('panels:project_detail', args=(project.id,)))
    assert Project.objects.count() == 1


@pytest.mark.parametrize(
    'param_project, expected_status',
    (
        ('project', HTTPStatus.OK),
        ('unpublished_project', HTTPStatus.OK),
        ('alien_project', HTTPStatus.OK),
        ('alien_unpublished_project', HTTPStatus.NOT_FOUND),
        ('alien_unpublished_coauthor_project', HTTPStatus.OK),
    )
)
def test_auhtor_can_view_panel(
    author_client, panels, param_project, expected_status
):
    response = author_client.get(
        reverse('panels:panel_detail', args=(panels[param_project].id,)))
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'param_project, expected_status',
    (
        ('project', HTTPStatus.FOUND),
        ('unpublished_project', HTTPStatus.FOUND),
        ('alien_project', HTTPStatus.NOT_FOUND),
        ('alien_unpublished_project', HTTPStatus.NOT_FOUND),
        ('alien_unpublished_coauthor_project', HTTPStatus.FOUND),
    )
)
def test_author_can_create_panel(
    request, author_client, param_project, expected_status,
    panel_create_form_data
):
    param_project = request.getfixturevalue(param_project)
    response = author_client.post(
        reverse('panels:panel_create', args=(param_project.id,)),
        data=panel_create_form_data
    )
    assert response.status_code == expected_status
    if expected_status == HTTPStatus.FOUND:
        assertRedirects(
            response,
            reverse('panels:project_detail', args=(param_project.id,))
        )
        assert param_project.panels.count() == 1
        panel = param_project.panels.get()
        assert panel.name == panel_create_form_data['name']
        assert panel.function_type == panel_create_form_data['function_type']
        assert panel.description == panel_create_form_data['description']


def test_cant_create_panel_with_nonunique_name_in_project(
    author_client, project, panel, panel_create_form_data
):
    panel_create_form_data['name'] = panel.name
    response = author_client.post(
        reverse('panels:panel_create', args=(project.id,)),
        data=panel_create_form_data
    )
    assert response.status_code == HTTPStatus.OK
    assert project.panels.count() == 1
    form = response.context['form']
    assert not form.is_valid()
    assert 'name' in form.errors