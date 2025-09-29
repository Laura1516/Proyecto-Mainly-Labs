from django.db import models
from apps.accounts.models import CustomUser
from datetime import datetime


# Create your models here.
class Course(models.Model):

    MODALITY_CHOICES = [
        ('online', 'online'),
        ('personal' 'personal')
    ]
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=2000)
    created_by = models.DateField(auto_now=True)
    modality = models.CharField(max_length=20, choices=MODALITY_CHOICES)


class UserCourseProgress(models.Model): #muestra el avance de cada user para cada curso.
    user = models.ForeignKey(CustomUser)
    course = models.ForeignKey(Course)
    date_started = models.DateField(blank=True, null=True)
    date_finished = models.DateField(blank=True, null=True)
    duration = models.DateField(blank=True, null=True)

    def save(self):
        if self.date_started and self.date_finished:
            durantion = self.date_finished - self.date_started
            self.duration = UserCourseProgress.objects.create(duration=durantion.days)
            super().save()


class certificate(models.Model):
    pass
