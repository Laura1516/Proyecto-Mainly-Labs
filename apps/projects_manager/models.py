from django.db import models
from apps.accounts.models import CustomUser


# Create your models here.
class Project(models.Model):
    STATE_CHOICES = [
        ('complete', 'complete'),
        ('incomplete', 'incomplete'),
    ]

    PRIORITY_CHOICES = [
        ('high', 'high'),
        ('medium', 'medium'),
        ('low', 'low')
    ]

    name = models.CharField(max_length=100)
    description = models.TextField(max_length=2000)
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default='incomplete')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='high')
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"Proyect: {self.name}"


class ProjectUser(models.Model):
    """
    helps to understand and provides a very detailed info about
    the role for each user on each task.
    """
    ROLE_CHOICES = [
        ("creator", "creator"),
        ("manager", "manager"),
        ("collaborator", "collaborator"),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='collaborator')

    class Meta:
        unique_together = ("user", "project")

    def __str__(self):
        return f"{self.user.username} - {self.project.name} [{self.role}]"
