from django.db import models
from accounts.models import User
from django.conf import settings

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Employee(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='employee_profile'
    )
    department = models.ForeignKey(
        'Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    position = models.CharField(max_length=100, null=True, blank=True)
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    hire_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.position}"