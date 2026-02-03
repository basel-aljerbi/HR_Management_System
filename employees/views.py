from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Employee
from .serializers import EmployeeSerializer
from .permissions import IsHR, IsEmployee
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import EmployeeSerializer

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated, IsHR]

    def get_queryset(self):
        return Employee.objects.select_related('user', 'department')
    
class MyProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        employee = request.user.employee_profile
        serializer = EmployeeSerializer(employee)
        return Response(serializer.data)