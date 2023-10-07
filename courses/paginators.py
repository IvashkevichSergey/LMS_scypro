from rest_framework.pagination import PageNumberPagination


class SimplePaginator(PageNumberPagination):
    """Класс для добавления пагинации"""
    page_size = 5
