from django.conf import settings
from django.core.paginator import Paginator

NUMBER_OF_POSTS_DISPLAYED = settings.NUMBER_OF_POSTS_DISPLAYED


def get_page_paginator(queryset, request):
    paginator = Paginator(queryset, NUMBER_OF_POSTS_DISPLAYED)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return {
        'page_number': page_number,
        'page_obj': page_obj,
    }
