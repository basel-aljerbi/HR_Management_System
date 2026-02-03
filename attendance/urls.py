from django.urls import path
from .views import CheckInView, CheckOutView

urlpatterns = [
    path('attendance/check-in/', CheckInView.as_view()),
    path('attendance/check-out/', CheckOutView.as_view()),
]