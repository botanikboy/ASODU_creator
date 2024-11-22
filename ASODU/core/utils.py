from django.core.paginator import Paginator

from django.conf import settings


def transliterate(any_string: str) -> str:
    return any_string.translate(str.maketrans(
        "абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ",
        "abvgdeejzijklmnoprstufhzcss_y_euaABVGDEEJZIJKLMNOPRSTUFHZCSS_Y_EUA"
    ))


def paginator_create(objects_list, page_number):
    paginator = Paginator(objects_list, settings.OBJECTS_COUNT_ON_PAGE)
    return paginator.get_page(page_number)
