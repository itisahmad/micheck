from django.contrib import admin
from .models import Show, Spot, Coupon, Booking


@admin.register(Show)
class ShowAdmin(admin.ModelAdmin):
    list_display = ('date', 'label')
    list_filter = ('date',)


class SpotInline(admin.TabularInline):
    model = Spot
    extra = 0


@admin.register(Spot)
class SpotAdmin(admin.ModelAdmin):
    list_display = ('show', 'time', 'duration_minutes', 'price', 'spot_type', 'max_slots', 'booked_count')
    list_filter = ('show__date',)
    search_fields = ('spot_type',)

    def booked_count(self, obj):
        return obj.booked_count
    booked_count.short_description = 'Booked'


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'min_spots', 'discount_type', 'discount_value', 'is_active')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('performer_name', 'email', 'spot', 'amount_paid', 'created_at')
    list_filter = ('created_at', 'spot__show__date')
    search_fields = ('performer_name', 'email')
