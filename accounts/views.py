from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import User
from employees.permissions import IsHR

class ChangeUserRoleView(APIView):
    permission_classes = [IsAuthenticated, IsHR]

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