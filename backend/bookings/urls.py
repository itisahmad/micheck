from django.urls import path
from . import views

urlpatterns = [
    path('', views.health),
    path('shows/', views.show_list),
    path('spots/', views.spot_list),
    path('coupon/validate/', views.validate_coupon),
    path('bookings/', views.create_booking),
    path('create-order/', views.create_order),
    path('verify-payment/', views.verify_payment),
    path('create-superuser/', views.create_superuser),
]
