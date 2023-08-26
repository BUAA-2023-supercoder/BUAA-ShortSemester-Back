from django.db import models

# Create your models here.
class Project(models.Model):
    team = models.ForeignKey('TeamApi.Team', on_delete=models.CASCADE)
    projectName = models.CharField(max_length=128, null=False)
    isDelete = models.BooleanField(default=False)
    image = models.ImageField(upload_to='ProjectProfile/', default='ProjectProfile/1.jpg')


class Document(models.Model):
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    documentName = models.CharField(max_length=128, null=False)
    context = models.TextField(null=True)
    lastEditTime = models.DateTimeField(auto_now_add=True)
    lastEditPerson = models.EmailField(null=True)


class PrototypePage(models.Model):
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    prototypeName = models.CharField(max_length=128, null=False)
    context = models.TextField(null=True)
    lastEditTime = models.DateTimeField(auto_now_add=True)
    lastEditPerson = models.EmailField(null=True)
    onEdit = models.BooleanField(default=True)

class ShareLink(models.Model):
    str = models.CharField(primary_key=True, max_length=128)
    document = models.ForeignKey('Document', on_delete=models.CASCADE)
    isWrite = models.BooleanField(default=False)
    createTime = models.DateTimeField(auto_now_add=True)
    validity = models.DateTimeField(null=True)
