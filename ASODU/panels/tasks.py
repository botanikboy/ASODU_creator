import io
import logging

import xlsxwriter
from celery import shared_task
from django.core.cache import cache

logger = logging.getLogger(__name__)

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


@shared_task
def generate_excel_report(panels: list[dict], report_key: str):
    logger.info('Начало выполнения задачи по отчету.')
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
            panel['description'],
            panel['name'],
            'шт.',
            1
        )
        worksheet.write_row(row, col, row_data)
        row += 1

        equipment = panel['amounts']
        for item_num, item in enumerate(equipment, start=1):
            worksheet.write_row(
                row, col,
                (f'{panel_num}.{item_num}.',) + (
                    item['equipment']['vendor']['name'],
                    item['equipment']['description'],
                    item['equipment']['code'],
                    item['equipment']['units'],
                    item['amount']
                ))
            row += 1
        row += 1

    workbook.close()
    buffer.seek(0)
    cache.set(f'report:{report_key}', buffer.read(), timeout=600)
    cache.set(f"report_status:{report_key}", "ready", timeout=600)
    return report_key
