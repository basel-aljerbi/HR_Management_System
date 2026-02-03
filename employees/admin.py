from django.contrib import admin
from .models import Employee, Department

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'get_role',
        'department',
        'position',
        'basic_salary',
    )

    def get_role(self, obj):
        return obj.user.role

    get_role.short_description = 'Role'
admin.site.register(Department)