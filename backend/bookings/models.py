from django.db import models


class Show(models.Model):
    """A show date - groups spots by day."""
    date = models.DateField(unique=True)
    label = models.CharField(max_length=100, blank=True)  # e.g. "Tue, 10 February"

    class Meta:
        ordering = ['date']

    def __str__(self):
        return self.label or str(self.date)


class Spot(models.Model):
    """A bookable performance slot within a show."""
    show = models.ForeignKey(Show, on_delete=models.CASCADE, related_name='spots')
    time = models.TimeField()
    duration_minutes = models.PositiveSmallIntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2, default=150)
    spot_type = models.CharField(max_length=100, blank=True)  # e.g. "Competitive Mic", "Open Mic"
    max_slots = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ['show__date', 'time']
        unique_together = [['show', 'time']]

    def __str__(self):
        return f"{self.show.date} {self.time} ({self.duration_minutes} mins)"

    @property
    def booked_count(self):
        return self.bookings.count()

    @property
    def is_full(self):
        return self.booked_count >= self.max_slots

    @property
    def spots_remaining(self):
        return max(0, self.max_slots - self.booked_count)


class Coupon(models.Model):
    """Discount coupon for bulk or promotional booking."""
    code = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=200, blank=True)
    min_spots = models.PositiveSmallIntegerField(default=0)  # minimum spots to use
    discount_type = models.CharField(max_length=20, choices=[
        ('fixed', 'Fixed amount per spot'),
        ('percent', 'Percentage off'),
    ], default='fixed')
    discount_value = models.DecimalField(max_digits=8, decimal_places=2)  # amount or percentage
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.code


class Booking(models.Model):
    """A performer's booking of one or more spots (one row per spot)."""
    spot = models.ForeignKey(Spot, on_delete=models.CASCADE, related_name='bookings')
    performer_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    coupon_used = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_id = models.CharField(max_length=100, blank=True, null=True)  # Razorpay payment ID
    payment_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ], default='pending')
    booking_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.performer_name} - {self.spot}"


class RazorpayLog(models.Model):
    """Track all Razorpay API calls and responses for debugging."""
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='razorpay_logs', null=True, blank=True)
    api_type = models.CharField(max_length=20, choices=[
        ('pre_booking', 'Pre-Booking'),
        ('create_order', 'Create Order'),
        ('verify_payment', 'Verify Payment'),
        ('payment_cancelled', 'Payment Cancelled'),
    ])
    request_data = models.JSONField(default=dict)
    response_data = models.JSONField(default=dict)
    status_code = models.IntegerField(null=True, blank=True)
    success = models.BooleanField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Razorpay Log"
        verbose_name_plural = "Razorpay Logs"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.api_type} - {self.booking.performer_name if self.booking else 'No Booking'} - {self.created_at}"


class SiteSettings(models.Model):
    """Site-wide settings that can be managed from admin."""
    maintenance_mode = models.BooleanField(default=False, help_text="Enable maintenance mode to take the site down")
    maintenance_message = models.TextField(default="We are currently under maintenance. Please check back soon.", help_text="Message to show when site is under maintenance")
    
    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"
    
    def __str__(self):
        return "Site Settings"
    
    @classmethod
    def get_settings(cls):
        settings_obj, created = cls.objects.get_or_create(pk=1)
        return settings_obj
