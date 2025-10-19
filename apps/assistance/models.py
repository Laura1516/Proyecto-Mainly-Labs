from django.db import models

# Create your models here.
from django.db import models
from apps.hr.models import Employee
from apps.accounts.models import CustomUser
from apps.projects.models import Project

from django.utils import timezone


# Create your models here.
class AssistanceRecord(models.Model):

    MODALITY_CHOICES = [
        ('presencial', 'presencial'),
        ('remoto', 'remoto'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="assistance_records")
    check_in = models.DateTimeField(auto_now_add=True)
    modality = models.CharField(max_length=20,choices=MODALITY_CHOICES)
    check_out = models.DateTimeField(null=True, blank=True)
    user_inside = models.BooleanField(default=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
    duration = models.DurationField(null=True, blank=True)

    def check_out_now(self): 
        if not self.check_out:
            self.check_out = timezone.now()
            self.save_full_record()

    def save_full_record(self):
        if self.check_out and not self.duration:
            self.duration = self.check_out - self.check_in
            self.user_inside = False
        super().save()


    #Falta definir metodo para contabilizar horas en cada proyecto y usuario.

    def __str__(self):
        return f"{self.employee}, Last Check in: {self.check_in}"
