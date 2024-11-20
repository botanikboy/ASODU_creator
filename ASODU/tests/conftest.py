import pytest

from panels.models import Panel, Project


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(
        username='Author', email='author@mail.com')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def project(author):
    project = Project.objects.create(
        name='project_test',
        author=author,
    )
    return project


@pytest.fixture
def panel(project):
    panel = Panel.objects.create(
        name='panel test',
        description='panel desc test',
        project=project,
    )
    return panel
