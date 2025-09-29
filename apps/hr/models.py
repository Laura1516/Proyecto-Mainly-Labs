from django.db import models
from django.utils import timezone
from apps.accounts.models import CustomUser
from typing import List

# Create your models here.
class EmployeeRecord(models.Model):
    #estado_laboral
    charge = models.CharField(max_length=50)
    date_hired = models.DateTimeField(max_length=timezone.now)
    supervisor = models.ForeignKey(CustomUser) #user role sup

class LeaveRequest(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date_start = models.DateField()
    date_finish = models.DateField()
    request_state = models.CharField()

class PerformanceReview(models.Model):
    user = models.ForeignKey(CustomUser)
    evaluted_by = models.CharField(CustomUser) #user role trainer...
    score = models.CharField()


class Payroll(models.Model):
    user = models.ForeignKey(CustomUser)
    month = models.DateField()
    amount = models.IntegerField()

    def payroll_pdf(self):
        pass


class Meeting(models.Model):
    title = models.CharField(max_length=50)
    date_meeting = models.DateTimeField()
    notes = models.TextField(max_length=2000)
    guests = List[CustomUser.username]


    def __str__(self):
        return self.title