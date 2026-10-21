"""API views for public and admin catalog endpoints.
Exposes list detail and management views for tours categories and guides.
Delegates business logic to the catalog services layer.
"""

from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalog.serializers import (
    CategorySerializer,
    CategoryWriteSerializer,
    FaqWriteSerializer,
    GuideSerializer,
    GuideWriteSerializer,
    TourDetailSerializer,
    TourFaqSerializer,
    TourImageCreateSerializer,
    TourImageSerializer,
    TourStatusSerializer,
    TourSummarySerializer,
    TourWriteSerializer,
)
from apps.catalog.services import (
    add_tour_image,
    create_category,
    create_faq,
    create_guide,
    create_tour,
    delete_faq,
    delete_tour_image,
    get_guide,
    get_tour,
    list_admin_tours,
    list_categories,
    list_tours,
    set_tour_status,
    update_faq,
    update_guide,
    update_tour,
)
from apps.core.pagination import ApiPagination
from apps.core.permissions import IsAdmin


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


class AdminTourListCreateView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        filters = {
            "status": request.query_params.get("status"),
            "search": request.query_params.get("search"),
        }
        tours = list_admin_tours(filters)
        paginator = ApiPagination()
        page = paginator.paginate_queryset(tours, request, view=self)
        serializer = TourSummarySerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = TourWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tour = create_tour(serializer.validated_data, user=request.user)
        detail_serializer = TourDetailSerializer(tour)
        return Response(detail_serializer.data, status=status.HTTP_201_CREATED)


class AdminTourUpdateView(APIView):
    permission_classes = [IsAdmin]

    def put(self, request, pk):
        serializer = TourWriteSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        tour = update_tour(pk, serializer.validated_data, user=request.user)
        detail_serializer = TourDetailSerializer(tour)
        return Response(detail_serializer.data, status=status.HTTP_200_OK)


class AdminTourStatusView(APIView):
    permission_classes = [IsAdmin]

    def patch(self, request, pk):
        serializer = TourStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = set_tour_status(pk, serializer.validated_data["status"])
        return Response(result, status=status.HTTP_200_OK)


class AdminTourImageCreateView(APIView):
    permission_classes = [IsAdmin]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, pk):
        serializer = TourImageCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        image = add_tour_image(
            pk,
            serializer.validated_data["image"],
            alt_text=serializer.validated_data.get("alt_text", ""),
            sort_order=serializer.validated_data.get("sort_order", 0),
        )
        res = TourImageSerializer(image)
        return Response(res.data, status=status.HTTP_201_CREATED)


class AdminTourImageDeleteView(APIView):
    permission_classes = [IsAdmin]

    def delete(self, request, pk):
        result = delete_tour_image(pk)
        return Response(result, status=status.HTTP_200_OK)


class AdminFaqCreateView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, pk):
        serializer = FaqWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        faq = create_faq(pk, serializer.validated_data)
        return Response(TourFaqSerializer(faq).data, status=status.HTTP_201_CREATED)


class AdminFaqDetailView(APIView):
    permission_classes = [IsAdmin]

    def put(self, request, pk):
        serializer = FaqWriteSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        faq = update_faq(pk, serializer.validated_data)
        return Response(TourFaqSerializer(faq).data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        result = delete_faq(pk)
        return Response(result, status=status.HTTP_200_OK)


class AdminGuideCreateView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request):
        serializer = GuideWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        guide = create_guide(serializer.validated_data)
        return Response(GuideSerializer(guide).data, status=status.HTTP_201_CREATED)


class AdminGuideUpdateView(APIView):
    permission_classes = [IsAdmin]

    def put(self, request, pk):
        serializer = GuideWriteSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        guide = update_guide(pk, serializer.validated_data)
        return Response(GuideSerializer(guide).data, status=status.HTTP_200_OK)


class AdminCategoryCreateView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request):
        serializer = CategoryWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        category = create_category(serializer.validated_data["name"])
        return Response(CategorySerializer(category).data, status=status.HTTP_201_CREATED)
