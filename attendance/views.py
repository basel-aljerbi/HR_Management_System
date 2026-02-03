from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.utils.dateparse import parse_date
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import Attendance
from .serializers import AttendanceSerializer
from employees.models import Employee
from rest_framework.generics import ListAPIView
from datetime import date, datetime
from django.db.models import Count
from employees.permissions import IsHR
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class CheckInView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Employee check-in",
        operation_description=(
            "Allows an employee to check in once per day. "
            "Only users with EMPLOYEE role are allowed."
        ),
        responses={
            200: openapi.Response(
                description="Check-in successful",
                examples={
                    "application/json": {
                        "message": "Check-in successful"
                    }
                }
            ),
            400: openapi.Response(
                description="Already checked in",
                examples={
                    "application/json": {
                        "error": "Already checked in"
                    }
                }
            ),
            403: openapi.Response(
                description="Only employees can check in",
                examples={
                    "application/json": {
                        "error": "Only employees can check in"
                    }
                }
            ),
        },
        security=[{"Bearer": []}]
    )
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

    @swagger_auto_schema(
        operation_summary="Employee check-out",
        operation_description=(
            "Allows an employee to check out after checking in on the same day. "
            "Only users with EMPLOYEE role are allowed."
        ),
        responses={
            200: openapi.Response(
                description="Check-out successful",
                examples={
                    "application/json": {
                        "message": "Check-out successful"
                    }
                }
            ),
            400: openapi.Response(
                description="No check-in found or already checked out",
                examples={
                    "application/json": {
                        "error": "No check-in found"
                    }
                }
            ),
            403: openapi.Response(
                description="Only employees can check out",
                examples={
                    "application/json": {
                        "error": "Only employees can check out"
                    }
                }
            ),
        },
        security=[{"Bearer": []}]
    )
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

@swagger_auto_schema(
    operation_summary="Attendance history",
    operation_description=(
        "Returns attendance records.\n\n"
        "- EMPLOYEE: can see only their own attendance.\n"
        "- HR: can see attendance for all employees or filter by employee ID.\n"
        "- Optional filters: date, employee (HR only)."
    ),
    manual_parameters=[
        openapi.Parameter(
            name='employee',
            in_=openapi.IN_QUERY,
            description="Employee ID (HR only)",
            type=openapi.TYPE_INTEGER,
            required=False
        ),
        openapi.Parameter(
            name='date',
            in_=openapi.IN_QUERY,
            description="Filter by date (YYYY-MM-DD)",
            type=openapi.TYPE_STRING,
            format='date',
            required=False
        ),
    ],
    responses={
        200: openapi.Response(
            description="List of attendance records"
        ),
        403: openapi.Response(
            description="Unauthorized access"
        ),
    },
    security=[{"Bearer": []}]
)
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
    
@swagger_auto_schema(
    operation_summary="Attendance report",
    operation_description=(
        "HR-only endpoint.\n\n"
        "Generates attendance report for a specific employee "
        "within a date range.\n\n"
        "**Required query parameters:**\n"
        "- employee_id\n"
        "- from (YYYY-MM-DD)\n"
        "- to (YYYY-MM-DD)"
    ),
    manual_parameters=[
        openapi.Parameter(
            name='employee_id',
            in_=openapi.IN_QUERY,
            description="Employee ID",
            type=openapi.TYPE_INTEGER,
            required=True
        ),
        openapi.Parameter(
            name='from',
            in_=openapi.IN_QUERY,
            description="Start date (YYYY-MM-DD)",
            type=openapi.TYPE_STRING,
            format='date',
            required=True
        ),
        openapi.Parameter(
            name='to',
            in_=openapi.IN_QUERY,
            description="End date (YYYY-MM-DD)",
            type=openapi.TYPE_STRING,
            format='date',
            required=True
        ),
    ],
    responses={
        200: openapi.Response(
            description="Attendance report generated successfully",
            examples={
                "application/json": {
                    "employee": "ahmad",
                    "from": "2026-02-01",
                    "to": "2026-02-05",
                    "total_days": 5,
                    "present_days": 4,
                    "absent_days": 1,
                    "late_days": 2
                }
            }
        ),
        400: openapi.Response(description="Missing or invalid parameters"),
        403: openapi.Response(description="HR access only"),
    },
    security=[{"Bearer": []}]
)
class AttendanceReportView(APIView):
    permission_classes = [IsAuthenticated, IsHR]

    def get(self, request):
        employee_id = request.query_params.get('employee_id')
        from_date = request.query_params.get('from')
        to_date = request.query_params.get('to')

        if not all([employee_id, from_date, to_date]):
            return Response(
                {"error": "employee_id, from, to are required"},
                status=400
            )

        employee = Employee.objects.get(id=employee_id)

        records = Attendance.objects.filter(
            employee=employee,
            date__range=[from_date, to_date]
        )

        present_days = records.filter(check_in__isnull=False).count()

        late_days = records.filter(
            check_in__gt=datetime.strptime("09:00", "%H:%M").time()
        ).count()

        total_days = (
            datetime.fromisoformat(to_date).date() -
            datetime.fromisoformat(from_date).date()
        ).days + 1

        absent_days = total_days - present_days

        return Response({
            "employee": employee.user.username,
            "from": from_date,
            "to": to_date,
            "total_days": total_days,
            "present_days": present_days,
            "absent_days": absent_days,
            "late_days": late_days
        })