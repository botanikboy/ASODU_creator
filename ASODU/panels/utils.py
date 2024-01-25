from django.core.paginator import Paginator

from .constants import OBJECTS_COUNT_ON_PAGE


def paginator_create(objects_list, page_number):
    paginator = Paginator(objects_list, OBJECTS_COUNT_ON_PAGE)
    return paginator.get_page(page_number)
