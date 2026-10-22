"""API views for customer and administrative review management.
Exposes public tour reviews customer review submissions and admin review listings.
Delegates business logic and validation to the reviews services layer.
"""

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.pagination import ApiPagination
from apps.core.permissions import IsAdmin
from apps.reviews.serializers import (
    ReviewAdminSerializer,
    ReviewCreateSerializer,
    ReviewSerializer,
)
from apps.reviews.services import (
    create_review,
    list_admin_reviews,
    list_tour_reviews,
)


class TourReviewListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, tour_id):
        reviews = list_tour_reviews(tour_id, user=request.user)
        paginator = ApiPagination()
        page = paginator.paginate_queryset(reviews, request, view=self)
        serializer = ReviewSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class ReviewCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ReviewCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        review = create_review(
            request.user,
            serializer.validated_data["booking_id"],
            serializer.validated_data["rating"],
            serializer.validated_data.get("comment", ""),
        )
        return Response(ReviewSerializer(review).data, status=status.HTTP_201_CREATED)


class AdminReviewListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        reviews = list_admin_reviews(request.query_params)
        paginator = ApiPagination()
        page = paginator.paginate_queryset(reviews, request, view=self)
        serializer = ReviewAdminSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
