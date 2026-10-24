"""Views for booking API endpoints.
Handles customer price previews and booking creation.
"""

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.bookings.serializers import BookingCreateSerializer, BookingQuoteSerializer
from apps.bookings.services import calculate_booking_quote, create_booking
from apps.core.permissions import IsCustomer


class BookingQuoteView(APIView):
    permission_classes = [IsAuthenticated, IsCustomer]

    def post(self, request):
        serializer = BookingQuoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        quote = calculate_booking_quote(**serializer.validated_data)
        return Response(quote)


class BookingCreateView(APIView):
    permission_classes = [IsAuthenticated, IsCustomer]

    def post(self, request):
        serializer = BookingCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        booking = create_booking(
            user=request.user,
            **serializer.validated_data,
        )

        return Response(
            {
                "id": booking.id,
                "booking_reference": booking.booking_reference,
                "status": booking.status,
                "total_price": booking.total_price,
            },
            status=status.HTTP_201_CREATED,
        )
