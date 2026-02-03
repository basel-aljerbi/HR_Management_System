from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import User
from employees.permissions import IsHR
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class ChangeUserRoleView(APIView):
    permission_classes = [IsAuthenticated, IsHR]

    @swagger_auto_schema(
        operation_summary="Change user role",
        operation_description=(
            "HR-only endpoint.\n\n"
            "Allows HR to change a user's role to either HR or EMPLOYEE."
        ),
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['role'],
            properties={
                'role': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="New role for the user",
                    enum=['HR', 'EMPLOYEE']
                )
            }
        ),
        manual_parameters=[
            openapi.Parameter(
                name='user_id',
                in_=openapi.IN_PATH,
                description="User ID",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="Role updated successfully",
                examples={
                    "application/json": {
                        "message": "Role updated to HR"
                    }
                }
            ),
            400: openapi.Response(description="Invalid role"),
            403: openapi.Response(description="HR access only"),
            404: openapi.Response(description="User not found"),
        },
        security=[{"Bearer": []}]
    )
    def patch(self, request, user_id):
        new_role = request.data.get('role')

        if new_role not in ['HR', 'EMPLOYEE']:
            return Response(
                {"error": "Invalid role"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.get(id=user_id)
        user.role = new_role
        user.save()

        return Response(
            {"message": f"Role updated to {new_role}"}
        )