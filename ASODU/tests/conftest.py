from random import randint, sample

import pytest

from panels.models import (Equipment, EquipmentGroup, EquipmentPanelAmount,
                           Panel, Project, Vendor)
from panels.utils import amounts_by_group

EQUPMENT_GROUPS_COUNT = 2
VENDORS_COUNT = 3
EQUIPMENT_ITEMS_COUNT = 6
MAX_AMOUNT_IN_PANEL = 100
EQUIPMENT_ITEMS_IN_PANEL = (EQUIPMENT_ITEMS_COUNT * VENDORS_COUNT) // 2


@pytest.fixture
def vendors():
    data = [Vendor(
        name=f'vendor name {i}') for i in range(VENDORS_COUNT)]
    return Vendor.objects.bulk_create(data)


@pytest.fixture
def groups():
    data = [EquipmentGroup(
        title=f'equipment group name {i}',
        slug=f'slug{i}',
    ) for i in range(EQUPMENT_GROUPS_COUNT)]
    return EquipmentGroup.objects.bulk_create(data)


@pytest.fixture
def equipment(db, vendors, groups):
    groups_count = len(groups)
    data = [Equipment(
        description=f'equipment description {i}',
        code=f'code{i}',
        vendor=vendors[v],
        units='шт.',
        group=groups[i % groups_count]
    )
        for i in range(EQUIPMENT_ITEMS_COUNT)
        for v in range(VENDORS_COUNT)]
    return Equipment.objects.bulk_create(data)


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
            name=f'{key}_panel',
            description=f'{key}_panel_description',
            project=project_obj,
        )
        panels[key] = panel

    return panels


@pytest.fixture
def panels_contents(db, panels, equipment):
    created_objects = []
    for panel in panels.values():
        randomized_equipment_list = sample(equipment, k=len(equipment))
        data = [EquipmentPanelAmount(
            equipment=randomized_equipment_list[i],
            panel=panel,
            amount=randint(1, MAX_AMOUNT_IN_PANEL)
        ) for i in range(EQUIPMENT_ITEMS_IN_PANEL)]
        created_objects.extend(EquipmentPanelAmount.objects.bulk_create(data))
    return created_objects


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


@pytest.fixture
def coauthor_add_form_data(alien_author):
    return {
        'co_authors': f'{alien_author.id}',
    }


@pytest.fixture
def coauthor_empty_form_data():
    return {
        'co_authors': '',
    }


@pytest.fixture
def copy_panel_form_data(project):
    return {
        'name': 'new copied panel name',
        'description': 'new copied panel desc',
        'project': project.id
    }


@pytest.fixture
def edit_panel_contents_form_data(panels, panels_contents, equipment):
    forms = {}
    for key, panel in panels.items():
        grouped_amounts = amounts_by_group(panel)
        forms[key] = {}

        for group_id, amounts in grouped_amounts.items():
            group_prefix = f'group_{group_id.id if group_id else "no_group"}'
            forms[key][f'{group_prefix}-TOTAL_FORMS'] = str(len(amounts))
            forms[key][f'{group_prefix}-INITIAL_FORMS'] = str(len(amounts))
            forms[key][f'{group_prefix}-MIN_NUM_FORMS'] = '0'
            forms[key][f'{group_prefix}-MAX_NUM_FORMS'] = '1000'

            for i, amount in enumerate(amounts):
                forms[key][f'{group_prefix}-{i}-amount'] = amount.amount + 3
                forms[key][f'{group_prefix}-{i}-DELETE'] = ''
                forms[key][f'{group_prefix}-{i}-id'] = amount.id
            if amounts:
                forms[key][f'{group_prefix}-0-DELETE'] = True

        all_groups = EquipmentGroup.objects.all()
        missing_groups = all_groups.exclude(
            id__in=[g.id for g in grouped_amounts.keys() if g])
        for group in missing_groups:
            group_prefix = f'group_{group.id}'
            forms[key][f'{group_prefix}-TOTAL_FORMS'] = '0'
            forms[key][f'{group_prefix}-INITIAL_FORMS'] = '0'
            forms[key][f'{group_prefix}-MIN_NUM_FORMS'] = '0'
            forms[key][f'{group_prefix}-MAX_NUM_FORMS'] = '1000'
    return forms
