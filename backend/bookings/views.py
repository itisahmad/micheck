from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from django.conf import settings
import razorpay
import hashlib
import hmac
import time
from .models import Show, Spot, Coupon, SiteSettings
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
        data = request.data
        print(f"[RAZORPAY] [CREATE-ORDER] Request received: {data}")
        
        amount = request.data.get('amount')
        print(f"[RAZORPAY] [CREATE-ORDER] Amount: {amount}")
        
        if not amount:
            print(f"[RAZORPAY] [CREATE-ORDER] ERROR: Amount missing")
            return Response({'error': 'Amount is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        print(f"[RAZORPAY] [CREATE-ORDER] Razorpay Key ID: {settings.RAZORPAY_KEY_ID[:10]}..." if settings.RAZORPAY_KEY_ID else "[RAZORPAY] [CREATE-ORDER] ERROR: Razorpay Key ID not set")
        print(f"[RAZORPAY] [CREATE-ORDER] Razorpay Key Secret: {'SET' if settings.RAZORPAY_KEY_SECRET else 'NOT SET'}")
        
        if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
            print(f"[RAZORPAY] [CREATE-ORDER] ERROR: Razorpay keys not configured")
            return Response({
                'error': 'Razorpay keys not configured. Please set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET in environment.',
                'key_id_set': bool(settings.RAZORPAY_KEY_ID),
                'key_secret_set': bool(settings.RAZORPAY_KEY_SECRET),
                'key_id_value': settings.RAZORPAY_KEY_ID[:10] + "..." if settings.RAZORPAY_KEY_ID else None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Check if keys are placeholder values
        if settings.RAZORPAY_KEY_ID == "rzp_test_YourTestKeyIdHere" or settings.RAZORPAY_KEY_SECRET == "YourTestKeySecretHere":
            print(f"[RAZORPAY] [CREATE-ORDER] ERROR: Using placeholder Razorpay keys")
            return Response({
                'error': 'Please replace placeholder Razorpay keys with actual test keys from Razorpay dashboard.',
                'dashboard_url': 'https://dashboard.razorpay.com/app/keys'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Initialize Razorpay client
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        print(f"[RAZORPAY] [CREATE-ORDER] Razorpay client initialized")
        
        # Create order
        currency = request.data.get('currency', 'INR')
        receipt = request.data.get('receipt', f"receipt_{int(time.time())}")
        notes = request.data.get('notes', {})
        
        order_data = {
            'amount': amount,
            'currency': currency,
            'receipt': receipt,
            'notes': notes,
            'payment_capture': 1
        }
        
        print(f"[RAZORPAY] [CREATE-ORDER] Creating order with data: {order_data}")
        
        order = client.order.create(order_data)
        
        print(f"[RAZORPAY] [CREATE-ORDER] Order created successfully: {order}")
        
        return Response(order, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def verify_payment(request):
    """Verify Razorpay payment and create booking."""
    try:
        data = request.data
        print(f"[RAZORPAY] [VERIFY-PAYMENT] Request received: {data}")
        
        payment_id = request.data.get('razorpay_payment_id')
        order_id = request.data.get('razorpay_order_id')
        signature = request.data.get('razorpay_signature')
        booking_ids = request.data.get('booking_ids', '').split(',') if request.data.get('booking_ids') else []
        
        print(f"[RAZORPAY] [VERIFY-PAYMENT] Parsed data:")
        print(f"  payment_id: {payment_id}")
        print(f"  order_id: {order_id}")
        print(f"  signature: {signature}")
        print(f"  booking_ids: {booking_ids}")
        
        if not all([payment_id, order_id, signature]):
            print(f"[RAZORPAY] [VERIFY-PAYMENT] ERROR: Missing payment details")
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
            print(f"[RAZORPAY] [VERIFY-PAYMENT] ERROR: Razorpay keys not configured")
            return Response({
                'error': 'Razorpay keys not configured in backend',
                'key_id_set': bool(settings.RAZORPAY_KEY_ID),
                'key_secret_set': bool(settings.RAZORPAY_KEY_SECRET)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Check if keys are placeholder values
        if settings.RAZORPAY_KEY_ID == "rzp_test_YourTestKeyIdHere" or settings.RAZORPAY_KEY_SECRET == "YourTestKeySecretHere":
            print(f"[RAZORPAY] [VERIFY-PAYMENT] ERROR: Using placeholder Razorpay keys")
            return Response({
                'error': 'Please replace placeholder Razorpay keys in backend with actual test keys',
                'dashboard_url': 'https://dashboard.razorpay.com/app/keys'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Verify signature
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        print(f"[RAZORPAY] [VERIFY-PAYMENT] Razorpay client initialized for signature verification")
        
        # Generate signature string
        signature_string = f"{order_id}|{payment_id}"
        generated_signature = hmac.new(
            settings.RAZORPAY_KEY_SECRET.encode(),
            signature_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        print(f"[RAZORPAY] [VERIFY-PAYMENT] Signature verification:")
        print(f"  signature_string: {signature_string}")
        print(f"  generated_signature: {generated_signature}")
        print(f"  received_signature: {signature}")
        
        if generated_signature != signature:
            print(f"[RAZORPAY] [VERIFY-PAYMENT] ERROR: Invalid signature")
            return Response({'error': 'Invalid payment signature'}, status=status.HTTP_400_BAD_REQUEST)
        
        print(f"[RAZORPAY] [VERIFY-PAYMENT] Signature verified successfully")
        
        # Verify payment with Razorpay
        try:
            payment = client.payment.fetch(payment_id)
            print(f"[RAZORPAY] [VERIFY-PAYMENT] Payment details from Razorpay: {payment}")
            
            if payment['status'] != 'captured':
                print(f"[RAZORPAY] [VERIFY-PAYMENT] ERROR: Payment not captured. Status: {payment['status']}")
                return Response({'error': 'Payment not captured'}, status=status.HTTP_400_BAD_REQUEST)
                
            print(f"[RAZORPAY] [VERIFY-PAYMENT] Payment captured successfully")
        except Exception as e:
            print(f"[RAZORPAY] [VERIFY-PAYMENT] ERROR: Payment verification failed: {str(e)}")
            return Response({'error': f'Payment verification failed: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update existing bookings after successful payment
        if not booking_ids:
            print(f"[RAZORPAY] [VERIFY-PAYMENT] ERROR: No booking IDs provided")
            return Response({'error': 'No booking IDs provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get existing bookings
        bookings = Booking.objects.filter(id__in=booking_ids, payment_status='pending', booking_status='pending')
        print(f"[RAZORPAY] [VERIFY-PAYMENT] Found {len(bookings)} bookings to update out of {len(booking_ids)} requested")
        
        if len(bookings) != len(booking_ids):
            print(f"[RAZORPAY] [VERIFY-PAYMENT] ERROR: Invalid booking IDs or bookings already processed")
            return Response({'error': 'Invalid booking IDs or bookings already processed'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update bookings with payment details
        for booking in bookings:
            print(f"[RAZORPAY] [VERIFY-PAYMENT] Updating booking {booking.id}: {booking.performer_name} - {booking.spot}")
            booking.payment_id = payment_id
            booking.payment_status = 'paid'
            booking.booking_status = 'confirmed'
            booking.save()
        
        print(f"[RAZORPAY] [VERIFY-PAYMENT] Successfully updated {len(bookings)} bookings")
        
        # Serialize the updated booking objects
        from .serializers import BookingSerializer
        booking_serializer = BookingSerializer(bookings, many=True)
        
        response_data = {
            'success': True,
            'message': f'Payment successful! Confirmed {len(bookings)} booking(s).',
            'payment_id': payment_id,
            'bookings': booking_serializer.data
        }
        
        print(f"[RAZORPAY] [VERIFY-PAYMENT] Success response: {response_data}")
        return Response(response_data, status=status.HTTP_200_OK)
        
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


@api_view(['POST'])
def create_pre_booking(request):
    """Create booking with pending status before payment."""
    try:
        data = request.data
        print(f"🔍 [PRE-BOOKING] Request received: {data}")
        
        spot_ids = data.get('spot_ids', '').split(',') if data.get('spot_ids') else []
        performer_name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()
        coupon_code = data.get('coupon_code', '').strip() or None
        amount = data.get('amount', 0)
        
        print(f"🔍 [PRE-BOOKING] Parsed data - Spots: {spot_ids}, Name: {performer_name}, Email: {email}, Phone: {phone}, Coupon: {coupon_code}, Amount: {amount}")
        
        # Validate required fields
        if not spot_ids or not performer_name or not email or not phone:
            return Response({
                'error': 'Missing required fields: spot_ids, name, email, phone'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get spots
        spots = Spot.objects.filter(id__in=spot_ids)
        print(f"🔍 [PRE-BOOKING] Found {len(spots)} spots out of {len(spot_ids)} requested")
        
        if len(spots) != len(spot_ids):
            print(f"🔍 [PRE-BOOKING] ERROR: Spots not found. Requested: {spot_ids}, Found: {[s.id for s in spots]}")
            return Response({
                'error': 'One or more spots not found'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check availability
        unavailable_spots = []
        for spot in spots:
            if spot.is_full:
                unavailable_spots.append(f"{spot.show_label or spot.show_date} - {spot.time}")
        
        print(f"🔍 [PRE-BOOKING] Availability check - Unavailable spots: {unavailable_spots}")
        
        if unavailable_spots:
            return Response({
                'error': 'Some spots are no longer available',
                'unavailable_spots': unavailable_spots
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate coupon if provided
        coupon = None
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code, is_active=True)
                print(f"🔍 [PRE-BOOKING] Coupon validated: {coupon_code}")
            except Coupon.DoesNotExist:
                print(f"🔍 [PRE-BOOKING] ERROR: Invalid coupon code: {coupon_code}")
                return Response({
                    'error': 'Invalid coupon code'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create bookings with pending status
        bookings = []
        for spot in spots:
            booking = Booking.objects.create(
                spot=spot,
                performer_name=performer_name,
                email=email,
                phone=phone,
                coupon_used=coupon,
                amount_paid=spot.price,
                payment_status='pending',
                booking_status='pending'
            )
            bookings.append(booking)
        
        print(f"🔍 [PRE-BOOKING] Created {len(bookings)} bookings with IDs: {[b.id for b in bookings]}")
        
        # Serialize bookings
        from .serializers import BookingSerializer
        booking_serializer = BookingSerializer(bookings, many=True)
        
        response_data = {
            'success': True,
            'message': f'Pre-booking created for {len(bookings)} spot(s)',
            'bookings': booking_serializer.data,
            'total_amount': sum(float(booking.amount_paid) for booking in bookings)
        }
        
        print(f"🔍 [PRE-BOOKING] Success response: {response_data}")
        return Response(response_data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        print(f"DEBUG: Error creating pre-booking: {str(e)}")
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def handle_payment_cancellation(request):
    """Handle payment cancellation - mark bookings as cancelled."""
    try:
        data = request.data
        print(f"[RAZORPAY] [PAYMENT-CANCELLED] Request received: {data}")
        
        booking_ids = request.data.get('booking_ids', '').split(',') if request.data.get('booking_ids') else []
        print(f"[RAZORPAY] [PAYMENT-CANCELLED] Booking IDs to cancel: {booking_ids}")
        
        if not booking_ids:
            print(f"[RAZORPAY] [PAYMENT-CANCELLED] ERROR: No booking IDs provided")
            return Response({'error': 'No booking IDs provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get existing bookings
        bookings = Booking.objects.filter(id__in=booking_ids, payment_status='pending', booking_status='pending')
        print(f"[RAZORPAY] [PAYMENT-CANCELLED] Found {len(bookings)} pending bookings to cancel")
        
        if not bookings.exists():
            print(f"[RAZORPAY] [PAYMENT-CANCELLED] ERROR: No pending bookings found")
            return Response({'error': 'No pending bookings found'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update bookings as cancelled
        for booking in bookings:
            print(f"[RAZORPAY] [PAYMENT-CANCELLED] Cancelling booking {booking.id}: {booking.performer_name} - {booking.spot}")
            booking.payment_status = 'cancelled'
            booking.booking_status = 'cancelled'
            booking.save()
        
        response_data = {
            'success': True,
            'message': f'Cancelled {len(bookings)} booking(s)'
        }
        
        print(f"[RAZORPAY] [PAYMENT-CANCELLED] Success: {response_data}")
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def maintenance_status(request):
    """Get maintenance mode status for frontend."""
    try:
        site_settings = SiteSettings.get_settings()
        print(f"DEBUG: Maintenance mode: {site_settings.maintenance_mode}, Message: {site_settings.maintenance_message}")
        return Response({
            'maintenance_mode': bool(site_settings.maintenance_mode),
            'maintenance_message': site_settings.maintenance_message
        })
    except Exception as e:
        print(f"DEBUG: Error getting maintenance status: {str(e)}")
        # If there's any error, default to not being in maintenance mode
        return Response({
            'maintenance_mode': False,
            'maintenance_message': 'Service temporarily unavailable',
            'error': str(e)
        }, status=status.HTTP_200_OK)
