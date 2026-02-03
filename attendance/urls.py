from django.urls import path
from .views import CheckInView, CheckOutView
from .views import AttendanceHistoryView

urlpatterns = [
    path('attendance/check-in/', CheckInView.as_view()),
    path('attendance/check-out/', CheckOutView.as_view()),
     path('attendance/history/', AttendanceHistoryView.as_view()),
]