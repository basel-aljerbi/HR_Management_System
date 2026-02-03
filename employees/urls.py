from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmployeeViewSet, MyProfileView

router = DefaultRouter()
router.register('employees', EmployeeViewSet)

urlpatterns = [
    path('employees/me/', MyProfileView.as_view()),
    path('', include(router.urls)),
    
]