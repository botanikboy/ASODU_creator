import io

import xlsxwriter
from django.db.models import Q
from django.shortcuts import get_object_or_404

from .models import Panel, Project


def excelreport(data: list, filename: str):
    buffer = io.BytesIO()
    workbook = xlsxwriter.Workbook(buffer)
    worksheet = workbook.add_worksheet()
    bold = workbook.add_format({'bold': 1})
    number_format = workbook.add_format({'num_format': '#,##0.00'})
    worksheet.set_row(0, 50)
    worksheet.set_column(1, 1, 25)
    worksheet.set_column(2, 2, 100)
    worksheet.set_column(3, 3, 35)
    worksheet.write('A1', '№ п/п', bold)
    worksheet.write('B1', 'Вендор', bold)
    worksheet.write('C1', 'Наименование и техническая характеристика', bold)
    worksheet.write('D1', 'Артикул/парт. номер', bold)
    worksheet.write('E1', 'Ед. изм.', bold)
    worksheet.write('F1', 'Кол-во.', bold)

    row = 1
    col = 0
    counter = 1
    for vendor, description, code, units, amount in data:
        if vendor == 'Инд. изготовление':
            worksheet.set_row(row, None, bold)
        worksheet.write(row, col, counter)
        worksheet.write(row, col + 1, vendor)
        worksheet.write(row, col + 2, description)
        worksheet.write(row, col + 3, code)
        worksheet.write(row, col + 4, units)
        worksheet.write(row, col + 5, float(amount), number_format)
        counter += 1
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

    panel = get_object_or_404(Panel, query, pk=id)
    return panel


def get_accessible_project(request, id: int):
    project = get_object_or_404(
        Project,
        Q(is_published=True)
        | Q(id__in=request.user.co_projects.values_list('id', flat=True))
        | Q(author=request.user),
        pk=id,
    )
    return project
