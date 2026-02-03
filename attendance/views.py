from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.utils.dateparse import parse_date
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import Attendance
from .serializers import AttendanceSerializer
from employees.models import Employee

class CheckInView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        if user.role != 'EMPLOYEE':
            return Response(
                {"error": "Only employees can check in"},
                status=status.HTTP_403_FORBIDDEN
            )

        employee = Employee.objects.get(user=user)
        today = timezone.now().date()

        attendance, created = Attendance.objects.get_or_create(
            employee=employee,
            date=today
        )

        if attendance.check_in:
            return Response(
                {"error": "Already checked in"},
                status=status.HTTP_400_BAD_REQUEST
            )

        attendance.check_in = timezone.now().time()
        attendance.save()

        return Response({"message": "Check-in successful"})
    
class CheckOutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        if user.role != 'EMPLOYEE':
            return Response(
                {"error": "Only employees can check out"},
                status=status.HTTP_403_FORBIDDEN
            )

        employee = Employee.objects.get(user=user)
        today = timezone.now().date()

        try:
            attendance = Attendance.objects.get(
                employee=employee,
                date=today
            )
        except Attendance.DoesNotExist:
            return Response(
                {"error": "No check-in found"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if attendance.check_out:
            return Response(
                {"error": "Already checked out"},
                status=status.HTTP_400_BAD_REQUEST
            )

        attendance.check_out = timezone.now().time()
        attendance.save()

        return Response({"message": "Check-out successful"})

class AttendanceHistoryView(ListAPIView):
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Attendance.objects.all()

        # Employee
        if user.role == 'EMPLOYEE':
            employee = Employee.objects.get(user=user)
            queryset = queryset.filter(employee=employee)

        # HR 
        elif user.role == 'HR':
            employee_id = self.request.query_params.get('employee')
            if employee_id:
                queryset = queryset.filter(employee_id=employee_id)

        # Date filters
        date = self.request.query_params.get('date')
        if date:
            parsed_date = parse_date(date)
            if parsed_date:
                queryset = queryset.filter(date=parsed_date)

        return queryset.order_by('-date')