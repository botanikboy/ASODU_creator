import io

import xlsxwriter
from django.db.models import Q, Prefetch
from django.shortcuts import get_object_or_404

from .models import Panel, Project, EquipmentPanelAmount


def excelreport(panels: list[Panel]):
    HEADER_TEXT = (
        '№ п/п',
        'Вендор',
        'Наименование и техническая характеристика',
        'Артикул/парт. номер',
        'Ед. изм.',
        'Кол-во.',
    )
    HEADER_COLOR = '#254E58'
    HEADER_TEXT_COLOR = 'white'
    BOLD_COLOR = '#88BDBC'

    buffer = io.BytesIO()
    workbook = xlsxwriter.Workbook(buffer)
    worksheet = workbook.add_worksheet()

    header_format = workbook.add_format({
        'bold': 1,
        'fg_color': HEADER_COLOR,
        'font_color': HEADER_TEXT_COLOR
    })
    bold = workbook.add_format({'bold': 1, 'fg_color': BOLD_COLOR})
    number_format = workbook.add_format({'num_format': '#,##0.00'})

    worksheet.set_row(0, 50, header_format)
    worksheet.set_column(1, 1, 25)
    worksheet.set_column(2, 2, 100)
    worksheet.set_column(3, 3, 35)
    worksheet.set_column(6, 6, None, number_format)

    row = 0
    col = 0

    worksheet.write_row(row, col, HEADER_TEXT)
    row += 1

    for panel_num, panel in enumerate(panels, start=1):
        worksheet.set_row(row, None, bold)
        row_data = (
            f'{panel_num}.',
            'Инд. изготовление',
            panel.description,
            panel.name,
            'шт.',
            1
        )
        worksheet.write_row(row, col, row_data)
        row += 1

        equipment = (
            panel.amounts
            .order_by('equipment__group', 'equipment__vendor__name')
            .values_list(
                'equipment__vendor__name',
                'equipment__description',
                'equipment__code',
                'equipment__units',
                'amount',
            )
        )
        for item_num, item in enumerate(equipment, start=1):
            worksheet.write_row(row, col, (f'{panel_num}.{item_num}.',) + item)
            row += 1
        row += 1

    workbook.close()
    buffer.seek(0)
    return buffer


def get_accessible_panel(request, id: int, published: bool = False):
    query = Q(
        project__in=request.user.co_projects.all()
    ) | Q(project__author=request.user)

    if published:
        query |= Q(project__is_published=True)

    panel = get_object_or_404(Panel.objects.prefetch_related(
        Prefetch(
            'amounts',
            queryset=EquipmentPanelAmount.objects.select_related(
                'equipment', 'equipment__vendor', 'equipment__group')
        ),
        'attachments'
    ).select_related('project'), query, pk=id)
    return panel


def get_accessible_project(request, id: int):
    project = get_object_or_404(
        Project.objects.select_related('author'),
        Q(is_published=True)
        | Q(id__in=request.user.co_projects.values_list('id', flat=True))
        | Q(author=request.user),
        pk=id,
    )
    return project
