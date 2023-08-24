from django.db import models


# Create your models here.
class User(models.Model):
    nickName = models.CharField(max_length=10)
    realName = models.CharField(max_length=10)
    email = models.CharField(max_length=20)
