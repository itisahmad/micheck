from rest_framework import serializers
from decimal import Decimal
from .models import Show, Spot, Coupon, Booking


class SpotSerializer(serializers.ModelSerializer):
    show_date = serializers.DateField(source='show.date', read_only=True)
    show_label = serializers.CharField(source='show.label', read_only=True)
    is_full = serializers.BooleanField(read_only=True)
    spots_remaining = serializers.IntegerField(read_only=True)

    class Meta:
        model = Spot
        fields = [
            'id', 'show', 'show_date', 'show_label', 'time', 'duration_minutes',
            'price', 'spot_type', 'max_slots', 'is_full', 'spots_remaining',
        ]


class ShowSerializer(serializers.ModelSerializer):
    spots = SpotSerializer(many=True, read_only=True)

    class Meta:
        model = Show
        fields = ['id', 'date', 'label', 'spots']


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ['code', 'min_spots', 'discount_type', 'discount_value', 'description']


class BookingCreateSerializer(serializers.Serializer):
    spot_ids = serializers.ListField(child=serializers.IntegerField(), min_length=1)
    performer_name = serializers.CharField(max_length=200)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20)
    coupon_code = serializers.CharField(max_length=50, required=False, allow_blank=True)

    def validate_spot_ids(self, value):
        spots = Spot.objects.filter(id__in=value)
        if spots.count() != len(value):
            raise serializers.ValidationError("One or more spot IDs are invalid.")
        for spot in spots:
            if spot.is_full:
                raise serializers.ValidationError(f"Spot {spot} is full.")
        return value

    def validate_coupon_code(self, value):
        if not value:
            return value
        try:
            coupon = Coupon.objects.get(code__iexact=value.strip(), is_active=True)
            return coupon
        except Coupon.DoesNotExist:
            raise serializers.ValidationError("Invalid or inactive coupon code.")

    def create(self, validated_data):
        spot_ids = validated_data['spot_ids']
        coupon = validated_data.get('coupon_code')
        spots = Spot.objects.filter(id__in=spot_ids)
        total = sum(s.price for s in spots)
        if coupon and isinstance(coupon, Coupon):
            if len(spot_ids) < coupon.min_spots:
                raise serializers.ValidationError(
                    f"This coupon requires at least {coupon.min_spots} spots."
                )
            if coupon.discount_type == 'fixed':
                total = coupon.discount_value * len(spot_ids)
            else:
                total = total * (Decimal('100') - coupon.discount_value) / Decimal('100')
        created = []
        for spot in spots:
            amount = total / len(spots) if spots.count() else total
            booking = Booking.objects.create(
                spot=spot,
                performer_name=validated_data['performer_name'],
                email=validated_data['email'],
                phone=validated_data['phone'],
                coupon_used=coupon if isinstance(coupon, Coupon) else None,
                amount_paid=amount,
            )
            created.append(booking)
        return {'bookings': created, 'total': total}


class BookingSerializer(serializers.ModelSerializer):
    spot_detail = SpotSerializer(source='spot', read_only=True)

    class Meta:
        model = Booking
        fields = ['id', 'spot', 'spot_detail', 'performer_name', 'email', 'phone', 'amount_paid', 'created_at']
