from django.core.paginator import Paginator
from django.conf import settings


def get_page_obj(post_list, page_number):
    paginator = Paginator(post_list, settings.POSTS_PER_PAGE)
    return paginator.get_page(page_number)
