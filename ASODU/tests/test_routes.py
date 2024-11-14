from http import HTTPStatus

from pytest_django.asserts import assertRedirects
from django.urls import reverse


def test_home_redirects_to_login_for_anonymous_user(client):
    url = reverse('panels:index')
    login_url = reverse('login')
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assert response.status_code == HTTPStatus.FOUND
    assertRedirects(response, expected_url)
