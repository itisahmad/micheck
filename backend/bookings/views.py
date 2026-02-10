from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from .models import Show, Spot, Coupon
from .serializers import ShowSerializer, SpotSerializer, CouponSerializer, BookingCreateSerializer


@api_view(['GET'])
def show_list(request):
    """List upcoming shows with their spots."""
    today = timezone.localdate()
    shows = Show.objects.filter(date__gte=today).prefetch_related('spots')
    serializer = ShowSerializer(shows, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def spot_list(request):
    """List all available spots (upcoming, not full)."""
    today = timezone.localdate()
    spots = Spot.objects.filter(show__date__gte=today).select_related('show').order_by('show__date', 'time')
    serializer = SpotSerializer(spots, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def validate_coupon(request):
    """Validate a coupon code and return discount info."""
    code = request.data.get('code', '').strip()
    spot_count = request.data.get('spot_count', 0)
    if not code:
        return Response({'valid': False, 'message': 'No code provided'})
    try:
        coupon = Coupon.objects.get(code__iexact=code, is_active=True)
        if spot_count < coupon.min_spots:
            return Response({
                'valid': False,
                'message': f'This coupon requires at least {coupon.min_spots} spots.',
            })
        return Response({
            'valid': True,
            'min_spots': coupon.min_spots,
            'discount_type': coupon.discount_type,
            'discount_value': str(coupon.discount_value),
            'description': coupon.description,
        })
    except Coupon.DoesNotExist:
        return Response({'valid': False, 'message': 'Invalid or inactive coupon code.'})


@api_view(['POST'])
def create_booking(request):
    """Create one or more bookings for a performer."""
    serializer = BookingCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    try:
        result = serializer.save()
        return Response({
            'success': True,
            'message': f'Successfully booked {len(result["bookings"])} spot(s).',
            'total': float(result['total']),
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
