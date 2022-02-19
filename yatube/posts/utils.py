from django.core.paginator import Paginator
from django.conf import settings
from django.contrib.auth.models import User


def get_page_obj(post_list, page_number):
    paginator = Paginator(post_list, settings.POSTS_PER_PAGE)
    return paginator.get_page(page_number)


def get_user_name(self):
    if self.first_name or self.last_name:
        return self.first_name + " " + self.last_name
    return f"[{self.username}]"


User.add_to_class("get_user_name", get_user_name)
