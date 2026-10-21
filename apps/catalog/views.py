"""API views for the public catalog endpoints.
Exposes list and detail views for tours categories and guides.
Delegates business logic to the catalog services layer.
"""

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalog.serializers import (
    CategorySerializer,
    GuideSerializer,
    TourDetailSerializer,
    TourSummarySerializer,
)
from apps.catalog.services import (
    get_guide,
    get_tour,
    list_categories,
    list_tours,
)
from apps.core.pagination import ApiPagination


class TourListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        filters = {
            "search": request.query_params.get("search"),
            "location": request.query_params.get("location"),
            "category_id": request.query_params.get("category_id"),
            "min_price": request.query_params.get("min_price"),
            "max_price": request.query_params.get("max_price"),
            "sort": request.query_params.get("sort", "newest"),
        }
        tours = list_tours(filters)
        paginator = ApiPagination()
        page = paginator.paginate_queryset(tours, request, view=self)
        serializer = TourSummarySerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class TourDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        tour = get_tour(pk, request.user)
        serializer = TourDetailSerializer(tour)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        categories = list_categories()
        serializer = CategorySerializer(categories, many=True)
        return Response({"items": serializer.data}, status=status.HTTP_200_OK)


class GuideDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        guide = get_guide(pk)
        serializer = GuideSerializer(guide)
        return Response(serializer.data, status=status.HTTP_200_OK)
