from django.urls import path
from . import views

urlpatterns = [
    path('', views.health),
    path('shows/', views.show_list),
    path('spots/', views.spot_list),
    path('coupon/validate/', views.validate_coupon),
    path('bookings/', views.create_booking),
    path('pre-booking/', views.create_pre_booking),
    path('create-order/', views.create_order),
    path('verify-payment/', views.verify_payment),
    path('payment-cancelled/', views.handle_payment_cancellation),
    path('receipt/<int:booking_id>/', views.download_receipt),
    path('create-superuser/', views.create_superuser),
    path('maintenance-status/', views.maintenance_status),
]
