"""Views for booking API endpoints.
Handles customer requests for booking price previews.
"""

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.bookings.serializers import BookingQuoteSerializer
from apps.bookings.services import calculate_booking_quote
from apps.core.permissions import IsCustomer


class BookingQuoteView(APIView):
    permission_classes = [IsAuthenticated, IsCustomer]

    def post(self, request):
        serializer = BookingQuoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        quote = calculate_booking_quote(**serializer.validated_data)
        return Response(quote)  # Create your views here.
