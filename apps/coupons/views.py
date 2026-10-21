"""API views for customer and admin coupon endpoints.
Exposes coupon validation listings and management operations.
Delegates business logic to the coupons services layer.
"""

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.pagination import ApiPagination
from apps.core.permissions import IsAdmin
from apps.coupons.serializers import (
    CouponCreateSerializer,
    CouponSerializer,
    CouponUpdateSerializer,
    CouponValidateSerializer,
)
from apps.coupons.services import (
    apply_coupon,
    create_coupon,
    list_coupons,
    update_coupon,
)


class CouponValidateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CouponValidateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        coupon, discount_amount, new_total = apply_coupon(
            serializer.validated_data["code"],
            serializer.validated_data["subtotal"],
        )
        return Response(
            {
                "code": coupon.code,
                "discount_type": coupon.discount_type,
                "discount_value": float(coupon.discount_value),
                "discount_amount": float(discount_amount),
                "new_total": float(new_total),
            },
            status=status.HTTP_200_OK,
        )


class AdminCouponListCreateView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        coupons = list_coupons()
        paginator = ApiPagination()
        page = paginator.paginate_queryset(coupons, request, view=self)
        serializer = CouponSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = CouponCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        coupon = create_coupon(serializer.validated_data)
        return Response(
            CouponSerializer(coupon).data,
            status=status.HTTP_201_CREATED,
        )


class AdminCouponUpdateView(APIView):
    permission_classes = [IsAdmin]

    def put(self, request, pk):
        serializer = CouponUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        coupon = update_coupon(pk, serializer.validated_data)
        return Response(
            CouponSerializer(coupon).data,
            status=status.HTTP_200_OK,
        )
