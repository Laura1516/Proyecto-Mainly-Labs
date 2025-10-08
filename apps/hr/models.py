from django.db import models
from django.utils import timezone
from apps.accounts.models import CustomUser

import uuid

# Create your models here.
class Employee(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=25)
    last_name = models.CharField(max_length=25)
    dni = models.CharField(max_length=21, unique=True)
    social_security = models.CharField(max_length=28, unique=True)
    bank_account = models.CharField(max_length=20, unique=True)
    phone_number = models.CharField(max_length=20)
    address = models.CharField(max_length=100)
    charge = models.CharField(max_length=30)
    employee_identification = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)


class LeaveRequest(models.Model):
    emplyee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date_start = models.DateField()
    date_finish = models.DateField()
    request_state = models.CharField(max_length=20, default='pending')

class PerformanceReview(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='reviews_received')
    evaluted_by = models.ForeignKey(Employee,on_delete=models.SET_NULL, null=True, related_name='reviews_given')
    evaluation_score = models.IntegerField()


class Payroll(models.Model):
    employee = models.ForeignKey(Employee, on_delete= models.CASCADE)
    month = models.DateField()
    salary = models.IntegerField()

    def payroll_pdf(self):
        pass

class Meeting(models.Model):
    host = models.ForeignKey(Employee, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    date_meeting = models.DateTimeField()
    notes = models.TextField(max_length=2000)
    guests = models.ManyToManyField(CustomUser, related_name="meetings")


    def __str__(self):
        return self.title