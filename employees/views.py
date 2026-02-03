from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Employee
from .serializers import EmployeeSerializer
from .permissions import IsHR, IsEmployee
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import EmployeeSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

@swagger_auto_schema(
    operation_summary="Manage employees (HR only)",
    operation_description=(
        "HR-only endpoint.\n\n"
        "Allows HR users to list, retrieve, create, update, and delete employees."
    ),
    responses={
        200: openapi.Response(description="Successful operation"),
        401: openapi.Response(description="Authentication required"),
        403: openapi.Response(description="HR access only"),
    },
    security=[{"Bearer": []}]
)
class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated, IsHR]

    def get_queryset(self):
        return Employee.objects.select_related('user', 'department')

@swagger_auto_schema(
    operation_summary="My profile",
    operation_description=(
        "Returns the profile of the currently authenticated employee."
    ),
    responses={
        200: openapi.Response(
            description="Employee profile",
            schema=EmployeeSerializer
        ),
        401: openapi.Response(description="Authentication required"),
    },
    security=[{"Bearer": []}]
)
class MyProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        employee = request.user.employee_profile
        serializer = EmployeeSerializer(employee)
        return Response(serializer.data)