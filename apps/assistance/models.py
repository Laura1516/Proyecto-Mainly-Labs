from django.db import models
from apps.accounts.models import CustomUser
from django.utils import timezone


# Create your models here.
class AssistanceRecord(models.Model):
    user = models.ForeignKey(CustomUser)
    check_in = models.DateTimeField(auto_now_add=True)
    check_out = models.DateTimeField(null=True, default=0)
    user_inside = models.BooleanField(default=False)
    duration = models.TimeField(default=0)

    def save(self):
        if not self.user_inside:
            record = AssistanceRecord.objects.create(
                self.check_out(timezone.now),
                self.duration(self.check_in - self.check_out)
            )

    def __str__(self):
        return f"{self.user}: Last Check in {self.check_in}"
