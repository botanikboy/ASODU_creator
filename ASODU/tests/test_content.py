from http import HTTPStatus

import pytest
from django.urls import reverse


def test_author_can_see_his_projects_on_main(
        author_client, project, alien_project, unpublished_project):
    response = author_client.get(reverse('panels:index'))
    projects = response.context.get('page_obj').paginator.object_list
    assert project in projects, 'проект автора должен быть на главной'
    assert (alien_project not in projects
            ), 'чужой проект не должен быть на главной'
    assert (unpublished_project in projects
            ), 'свой неопубликованный проект должен быть на главной'


def test_author_projects_list(
        author_client, project, alien_project, alien_unpublished_project,
        alien_unpublished_coauthor_project
):
    response = author_client.get(reverse('panels:project_list'))
    projects = response.context.get('page_obj').paginator.object_list
    assert project in projects, ''
    assert (alien_project in projects
            ), 'чужой опубликованный проект должен быть в списке'
    assert (alien_unpublished_project not in projects
            ), 'чужой неопубликованный проект не должен быть в списке'
    assert (alien_unpublished_coauthor_project in projects
            ), ('чужой неопубликованный проект в которым ты соавтор должен '
                'быть в списке')


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
def test_author_or_coauthor_can_see_project_details(
    author_client, expected_status, request, param_project
):
    param_project = request.getfixturevalue(param_project)
    response = author_client.get(
        reverse('panels:project_detail', args=(param_project.id,)))
    assert response.status_code == expected_status
