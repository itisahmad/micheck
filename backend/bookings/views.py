from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from django.conf import settings
import razorpay
import hashlib
import hmac
from .models import Show, Spot, Coupon
from .serializers import ShowSerializer, SpotSerializer, CouponSerializer, BookingCreateSerializer


@api_view(["GET"])
def health(request):
    """Health check for Vercel/serverless - no DB required."""
    return Response({"status": "ok", "message": "MicCheck API"})


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


@api_view(['POST'])
def create_order(request):
    """Create Razorpay order for payment."""
    try:
        amount = request.data.get('amount')
        currency = request.data.get('currency', 'INR')
        receipt = request.data.get('receipt')
        notes = request.data.get('notes', {})
        
        if not amount:
            return Response({'error': 'Amount is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if Razorpay keys are configured
        if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
            return Response({
                'error': 'Razorpay keys not configured. Please set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET in environment.',
                'key_id_set': bool(settings.RAZORPAY_KEY_ID),
                'key_secret_set': bool(settings.RAZORPAY_KEY_SECRET),
                'key_id_value': settings.RAZORPAY_KEY_ID[:10] + "..." if settings.RAZORPAY_KEY_ID else None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Check if keys are placeholder values
        if settings.RAZORPAY_KEY_ID == "rzp_test_YourTestKeyIdHere" or settings.RAZORPAY_KEY_SECRET == "YourTestKeySecretHere":
            return Response({
                'error': 'Please replace placeholder Razorpay keys with actual test keys from Razorpay dashboard.',
                'dashboard_url': 'https://dashboard.razorpay.com/app/keys'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Initialize Razorpay client
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        
        # Create order
        order_data = {
            'amount': amount,
            'currency': currency,
            'receipt': receipt,
            'notes': notes,
            'payment_capture': 1
        }
        
        order = client.order.create(order_data)
        
        return Response(order, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def verify_payment(request):
    """Verify Razorpay payment and create booking."""
    try:
        payment_id = request.data.get('razorpay_payment_id')
        order_id = request.data.get('razorpay_order_id')
        signature = request.data.get('razorpay_signature')
        
        name = request.data.get('name')
        email = request.data.get('email')
        phone = request.data.get('phone')
        spot_ids = request.data.get('spot_ids', [])
        coupon_code = request.data.get('coupon_code')
        
        # Debug logging
        print(f"Payment verification request:")
        print(f"  payment_id: {payment_id}")
        print(f"  order_id: {order_id}")
        print(f"  signature: {signature}")
        print(f"  name: {name}")
        print(f"  email: {email}")
        print(f"  phone: {phone}")
        print(f"  spot_ids: {spot_ids}")
        print(f"  coupon_code: {coupon_code}")
        
        if not all([payment_id, order_id, signature]):
            return Response({
                'error': 'Missing payment details',
                'missing_fields': {
                    'payment_id': bool(payment_id),
                    'order_id': bool(order_id),
                    'signature': bool(signature)
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if Razorpay keys are configured
        if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
            return Response({
                'error': 'Razorpay keys not configured in backend',
                'key_id_set': bool(settings.RAZORPAY_KEY_ID),
                'key_secret_set': bool(settings.RAZORPAY_KEY_SECRET)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Check if keys are placeholder values
        if settings.RAZORPAY_KEY_ID == "rzp_test_YourTestKeyIdHere" or settings.RAZORPAY_KEY_SECRET == "YourTestKeySecretHere":
            return Response({
                'error': 'Please replace placeholder Razorpay keys in backend with actual test keys',
                'dashboard_url': 'https://dashboard.razorpay.com/app/keys'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Verify signature
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        
        # Generate signature string
        signature_string = f"{order_id}|{payment_id}"
        generated_signature = hmac.new(
            settings.RAZORPAY_KEY_SECRET.encode(),
            signature_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        if generated_signature != signature:
            return Response({'error': 'Invalid payment signature'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify payment with Razorpay
        try:
            payment = client.payment.fetch(payment_id)
            if payment['status'] != 'captured':
                return Response({'error': 'Payment not captured'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'Payment verification failed: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create booking after successful payment
        booking_data = {
            'spot_ids': spot_ids,
            'performer_name': name,
            'email': email,
            'phone': phone,
            'coupon_code': coupon_code if coupon_code and coupon_code.strip() else None,
            'payment_id': payment_id,
            'payment_status': 'paid'
        }
        
        serializer = BookingCreateSerializer(data=booking_data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        result = serializer.save()
        
        # Serialize the booking objects
        from .serializers import BookingSerializer
        booking_serializer = BookingSerializer(result['bookings'], many=True)
        
        return Response({
            'success': True,
            'message': f'Payment successful! Booked {len(result["bookings"])} spot(s).',
            'total': float(result['total']),
            'payment_id': payment_id,
            'bookings': booking_serializer.data
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def create_superuser(request):
    """Create superuser for admin access (temporary for development)."""
    try:
        from django.contrib.auth.models import User
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email', '')
        
        if not username or not password:
            return Response({'error': 'Username and password required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(username=username).exists():
            return Response({'error': 'User already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.create_superuser(username, email, password)
        return Response({
            'success': True,
            'message': f'Superuser {username} created successfully',
            'login_url': '/admin/'
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
