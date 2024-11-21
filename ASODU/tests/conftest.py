import pytest

from panels.models import Panel, Project


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(
        username='Author', email='author@mail.com')


@pytest.fixture
def alien_author(django_user_model):
    return django_user_model.objects.create(
        username='Alien_Author', email='alien_author@mail.com')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def alien_author_client(alien_author, client):
    client.force_login(alien_author)
    return client


@pytest.fixture
def project(author):
    project = Project.objects.create(
        name='project_test',
        author=author,
    )
    return project


@pytest.fixture
def unpublished_project(author):
    project = Project.objects.create(
        name='unpub_project_test',
        author=author,
        is_published=False
    )
    return project


@pytest.fixture
def alien_project(alien_author):
    project = Project.objects.create(
        name='alien_project_test',
        author=alien_author,
    )
    return project


@pytest.fixture
def alien_unpublished_project(alien_author):
    project = Project.objects.create(
        name='alien_unpub_project_test',
        author=alien_author,
        is_published=False
    )
    return project


@pytest.fixture
def alien_unpublished_coauthor_project(alien_author, author):
    project = Project.objects.create(
        name='alien_unpub_coauthor_project_test',
        author=alien_author,
        is_published=False,
    )
    project.co_authors.set([author])
    return project


@pytest.fixture
def panel(project):
    panel = Panel.objects.create(
        name='panel test',
        description='panel desc test',
        project=project,
    )
    return panel


@pytest.fixture
def panels(
    project,
    unpublished_project,
    alien_project,
    alien_unpublished_project,
    alien_unpublished_coauthor_project
):
    panels = {}

    projects = {
        'project': project,
        'unpublished_project': unpublished_project,
        'alien_project': alien_project,
        'alien_unpublished_project': alien_unpublished_project,
        'alien_unpublished_coauthor_project':
            alien_unpublished_coauthor_project,
    }

    for key, project_obj in projects.items():
        panel = Panel.objects.create(
            name=f'{key}_test',
            description=f'{key}_description',
            project=project_obj,
        )
        panels[key] = panel

    return panels


@pytest.fixture
def project_create_form_data():
    return {
        'is_published': True,
        'name': 'project name',
        'description': 'project desc',
    }


@pytest.fixture
def project_edit_form_data():
    return {
        'is_published': False,
        'name': 'edited project name',
        'description': 'edited project desc',
    }


@pytest.fixture
def panel_create_form_data():
    return {
        'name': 'panel name',
        'function_type': 'general',
        'description': 'panel description',
    }


@pytest.fixture
def panel_edit_form_data():
    return {
        'name': 'edited panel name',
        'function_type': 'power',
        'description': 'edited panel description',
    }
