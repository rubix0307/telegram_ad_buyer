from django.core.handlers.wsgi import WSGIRequest

from .models import Category


class LazyCategories(object):
    def __iter__(self):
        return iter(Category.objects.filter(is_show=True))


def categories_processor(request: WSGIRequest):
    context = {'categories': LazyCategories()}
    return context
