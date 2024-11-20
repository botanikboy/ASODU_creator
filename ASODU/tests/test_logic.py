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
    expected_status, author
):
    param_project = request.getfixturevalue(param_project)
    response = author_client.post(
        reverse('panels:project_edit', args=(param_project.id,)),
        data=project_edit_form_data)
    assert response.status_code == expected_status
    param_project.refresh_from_db()
    # print(f'Исходный код ответа: {param_project.is_published}')
    if expected_status == HTTPStatus.FOUND:
        assertRedirects(
            response,
            reverse('panels:project_detail', args=(param_project.id,))
        )
