from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'param_client, expected_status',
    (
        ('client', HTTPStatus.FOUND),
        ('author_client', HTTPStatus.OK)
    )
)
@pytest.mark.parametrize(
    'name, data',
    (
        ('index', None),
        ('template_list', None),
        ('project_list', None),
        ('project_detail', 'project'),
        ('project_edit', 'project'),
        ('project_create', None),
        ('panel_detail', 'panel'),
        ('panel_create', 'project'),
        ('boq_download_project', 'project'),
        ('panel_edit', 'panel'),
        ('panel_edit_contents', 'panel'),
        ('panel_copy', 'panel'),
        ('boq_download_panel', 'panel'),
        ('file_add', 'panel'),
        ('add_author', 'project')
    )
)
def test_any_page_redirects_to_login_for_anonymous_user(
        client, name, data, request, param_client, expected_status):
    if data is not None:
        data = (request.getfixturevalue(data).pk,)
    url = reverse(f'panels:{name}', args=data)
    param_client = request.getfixturevalue(param_client)
    response = param_client.get(url)
    assert response.status_code == expected_status
    if expected_status == HTTPStatus.FOUND:
        login_url = reverse('users:login')
        expected_redirect_url = f'{login_url}?next={url}'
        assertRedirects(response, expected_redirect_url)


@pytest.mark.parametrize(
    'name, status_code',
    (
        ('users:signup', HTTPStatus.OK),
        ('users:login', HTTPStatus.OK),
        ('users:password_change_done', HTTPStatus.FOUND),
        ('users:password_reset_done', HTTPStatus.OK),
        ('users:password_reset_complete', HTTPStatus.OK)
    )
)
def test_users_service_pages_availible(client, name, status_code):
    response = client.get(reverse(name))
    assert response.status_code == status_code
