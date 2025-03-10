from django.conf import settings
from rest_framework import pagination


class CustomPagination(pagination.PageNumberPagination):
    page_size_query_param = 'limit'
    page_size = settings.PAGE_SIZE
