import io

import xlsxwriter
from django.core.paginator import Paginator

from .constants import OBJECTS_COUNT_ON_PAGE


def paginator_create(objects_list, page_number):
    paginator = Paginator(objects_list, OBJECTS_COUNT_ON_PAGE)
    return paginator.get_page(page_number)


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
