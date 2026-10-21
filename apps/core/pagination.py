"""
Custom pagination class for Kiwi Trails.
Provides page and page_size query parameter parsing with structured metadata.
"""

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from apps.core.exceptions import ValidationFailed


class ApiPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50

    def paginate_queryset(self, queryset, request, view=None):
        page_str = request.query_params.get(self.page_query_param)
        if page_str is not None:
            try:
                page_val = int(page_str)
                if page_val < 1:
                    raise ValueError
            except (ValueError, TypeError):
                raise ValidationFailed(
                    "Invalid page number.",
                    {"page": "Page must be a positive integer."},
                )

        page_size_str = request.query_params.get(self.page_size_query_param)
        if page_size_str is not None:
            try:
                page_size_val = int(page_size_str)
                if page_size_val < 1:
                    raise ValueError
            except (ValueError, TypeError):
                raise ValidationFailed(
                    "Invalid page size.",
                    {"page_size": "Page size must be a positive integer."},
                )

        try:
            return super().paginate_queryset(queryset, request, view)
        except Exception:
            raise ValidationFailed(
                "Invalid page.",
                {"page": "The requested page was not found."},
            )

    def get_paginated_response(self, data):
        return Response(
            {
                "items": data,
                "page": self.page.number,
                "page_size": self.get_page_size(self.request),
                "total": self.page.paginator.count,
            }
        )
