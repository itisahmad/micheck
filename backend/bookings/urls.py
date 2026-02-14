from django.urls import path
from . import views

urlpatterns = [
    path('', views.health),
    path('shows/', views.show_list),
    path('spots/', views.spot_list),
    path('coupon/validate/', views.validate_coupon),
    path('bookings/', views.create_booking),
]
