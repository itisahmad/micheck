from django.contrib import admin
from .models import Show, Spot, Coupon, Booking, SiteSettings, RazorpayLog


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
    list_display = ('performer_name', 'email', 'spot', 'amount_paid','payment_status','booking_status', 'created_at')
    list_filter = ('created_at', 'spot__show__date', 'payment_status', 'booking_status')
    search_fields = ('performer_name', 'email')


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('maintenance_mode', 'maintenance_message')
    list_filter = ('maintenance_mode',)

    def has_add_permission(self, request):
        # Only allow one settings object
        return not SiteSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(RazorpayLog)
class RazorpayLogAdmin(admin.ModelAdmin):
    list_display = ('api_type', 'booking', 'success', 'status_code', 'created_at')
    list_filter = ('api_type', 'success', 'created_at')
    search_fields = ('booking__performer_name', 'booking__email', 'error_message')
    readonly_fields = ('api_type', 'booking', 'request_data', 'response_data', 'status_code', 'success', 'error_message', 'created_at')
    ordering = ('-created_at',)
    list_per_page = 50
