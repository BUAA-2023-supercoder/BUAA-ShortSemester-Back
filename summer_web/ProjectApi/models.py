from django.db import models


# Create your models here.
class Project(models.Model):
    team = models.ForeignKey('TeamApi.Team', on_delete=models.CASCADE)
    projectName = models.CharField(max_length=128, null=False)
    isDelete = models.BooleanField(default=False)


class Document(models.Model):
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    documentName = models.CharField(max_length=128, null=False)


class PrototypePage(models.Model):
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    prototypeName = models.CharField(max_length=128, null=False)
