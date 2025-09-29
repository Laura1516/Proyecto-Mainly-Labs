from django.db import models
from apps.projects_manager.models import Project

# Create your models here.
class PurchaseOrder(models.Model):
    item = models.CharField(max_length=200)
    reference = models.IntegerField(max_length=20, unique=True)
    project = models.ForeignKey(Project)
    supplier = models.CharField(max_length=100)
    cost = models.IntegerField()

    def __str__(self):
        return f"Item: {self.item}"
