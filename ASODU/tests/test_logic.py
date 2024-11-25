from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects

from panels.models import Project, Panel


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


@pytest.mark.parametrize(
    'operation, name, form_data, expected_redirect',
    (
        ('edit', 'panel_edit', 'panel_edit_form_data', 'panel_detail'),
        ('create', 'panel_create', 'panel_create_form_data', 'project_detail')
    )
)
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
def test_author_can_create_and_edit_panel(
    author_client, panels, param_project, expected_status,
    form_data, request, name, operation, expected_redirect
):
    form_data = request.getfixturevalue(form_data)
    param_project_fixture = request.getfixturevalue(param_project)

    if operation == 'create':
        args = (param_project_fixture.id,)
    elif operation == 'edit':
        args = (panels[param_project].id,)
    panels_count = param_project_fixture.panels.count()

    response = author_client.post(
        reverse(f'panels:{name}', args=args), data=form_data)

    assert response.status_code == expected_status
    if expected_status == HTTPStatus.FOUND:
        assertRedirects(
            response,
            reverse(f'panels:{expected_redirect}', args=args)
        )
        assert param_project_fixture.panels.count() == (
            panels_count + (1 if operation == 'create' else 0))
        panel = param_project_fixture.panels.order_by('-id').first()
        assert panel.name == form_data['name']
        assert panel.function_type == form_data['function_type']
        assert panel.description == form_data['description']
    elif expected_status == HTTPStatus.NOT_FOUND:
        assert param_project_fixture.panels.count() == panels_count


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
def test_author_can_delete_panel(
    author_client, param_project, expected_status, panels, request
):
    assert Panel.objects.filter(pk=panels[param_project].id).exists()
    response = author_client.delete(
        reverse('panels:panel_delete', args=(panels[param_project].id,)))
    assert response.status_code == expected_status
    if expected_status == HTTPStatus.FOUND:
        assert not Panel.objects.filter(pk=panels[param_project].id).exists()
        param_project = request.getfixturevalue(param_project)
        assertRedirects(
            response,
            reverse('panels:project_detail', args=(param_project.id,))
        )


@pytest.mark.parametrize(
    'form_data',
    ('coauthor_empty_form_data',
     'coauthor_add_form_data')
)
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
def test_author_can_add_remove_coauthor(
    author_client, param_project, expected_status, form_data,
    request
):
    form_data = request.getfixturevalue(form_data)
    param_project = request.getfixturevalue(param_project)
    response = author_client.post(
        reverse('panels:add_author', args=(param_project.id,)),
        data=form_data)
    assert response.status_code == expected_status
    if expected_status == HTTPStatus.FOUND:
        updated_ids = ','.join(map(
            str, param_project.co_authors.values_list('id', flat=True)))
        assert form_data['co_authors'] == updated_ids
        assertRedirects(
            response,
            reverse('panels:project_detail', args=(param_project.id,))
        )


@pytest.mark.parametrize(
    'param_project, expected_status',
    (
        ('project', HTTPStatus.FOUND),
        ('unpublished_project', HTTPStatus.FOUND),
        ('alien_project', HTTPStatus.FOUND),
        ('alien_unpublished_project', HTTPStatus.NOT_FOUND),
        ('alien_unpublished_coauthor_project', HTTPStatus.FOUND),
    )
)
def test_author_can_copy_panel_to_his_project(
    author_client, panels, param_project, expected_status, panels_contents,
    copy_panel_form_data, project
):
    initial_panels_count = project.panels.count()
    panel = panels[param_project]
    response = author_client.post(
        reverse('panels:panel_copy', args=(panel.id,)),
        data=copy_panel_form_data
    )
    assert response.status_code == expected_status
    if expected_status == HTTPStatus.FOUND:
        assert project.panels.count() == initial_panels_count + 1
        last_added_panel = project.panels.order_by('id').last()
        assert last_added_panel.function_type == panel.function_type
        for amount in panel.amounts.all():
            assert last_added_panel.amounts.filter(
                equipment=amount.equipment, amount=amount.amount).exists()


@pytest.mark.skip
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
def test_panel_edit_contents(param_project, expected_status):
    pass


@pytest.mark.skip
def test_boq_download():
    pass


@pytest.mark.skip
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
def test_file_add(param_project, expected_status):
    pass


@pytest.mark.skip
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
def test_file_delete(param_project, expected_status):
    pass
