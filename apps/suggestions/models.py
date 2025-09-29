from django.db import models
from apps.accounts.models import CustomUser


# Create your models here.
class UserSuggestion(models.Model):

    STATE_CHOICES = [
        ('pending', 'pending'),
        ('accepted', 'accepted'),
        ('rejected', 'rejected')
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    description = models.TextField(max_length=2000)
    state = models.IntegerField(max_length=20, choices=STATE_CHOICES, default='pending')

    def __str__(self):
        return f"{self.user}: Suggestion {self.description}" #modificar esto.

class UserActivityProposal(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=2000)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}: Actitvity Proposal: {self.description}" #modificar esto.


class Vote(models.Model):
    user = models.ForeignKey(CustomUser)
    #falta mas logica.