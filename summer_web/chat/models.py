from django.db import models
from django.contrib.auth.models import User
class Team(models.Model):
    name = models.CharField(max_length=100)
    creator = models.ForeignKey('Member', on_delete=models.CASCADE, related_name='created_teams')

class Member(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=100)
    real_name = models.CharField(max_length=100)
    email = models.EmailField()
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)