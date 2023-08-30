from django.db import models

# Create your models here.
class Team(models.Model):
    creator = models.ForeignKey('UserApi.UserInfo', on_delete=models.CASCADE)
    name = models.CharField(max_length=128, null=False)
    profile = models.ImageField(upload_to="TeamProfile/", default="TeamProfile/default.png")

ROLE_ITEM = [
    (0, '创建者'),
    (1, '管理员'),
    (2, '普通用户')
]

class TeamMember(models.Model):
    member = models.ForeignKey('UserApi.UserInfo', on_delete=models.CASCADE)
    teamID = models.ForeignKey('Team', on_delete=models.CASCADE)
    role = models.IntegerField(choices=ROLE_ITEM, default=2)

TYPE_ITEM = [
    (0, 'text'),
    (1, 'image'),
    (2, 'file')
]

class TeamMessage(models.Model):
    type = models.IntegerField(choices=TYPE_ITEM, null=False)
    text = models.TextField(null=True)
    image = models.ImageField(upload_to='Images/', null=True)
    file = models.FileField(upload_to='Files/', null=True)
    fileName = models.CharField(max_length=128, null=True)
    sender = models.ForeignKey('UserApi.UserInfo', on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)
    team = models.ForeignKey('Team', on_delete=models.CASCADE)


class SingleMessage(models.Model):
    type = models.IntegerField(choices=TYPE_ITEM, null=False)
    text = models.TextField(null=True)
    image = models.ImageField(upload_to='Images/', null=True)
    file = models.FileField(upload_to='Files/', null=True)
    fileName = models.CharField(max_length=128, null=True)
    sendUser = models.ForeignKey('UserApi.UserInfo', on_delete=models.CASCADE, related_name='send_msg')
    receiveUser = models.ForeignKey('UserApi.UserInfo', on_delete=models.CASCADE, related_name='receive_msg')
    time = models.DateTimeField(auto_now_add=True)

class SingleUnread(models.Model):
    host = models.ForeignKey('UserApi.UserInfo', on_delete=models.CASCADE, related_name='host')
    guest = models.ForeignKey('UserApi.UserInfo', on_delete=models.CASCADE, related_name='guest')
    cnt = models.IntegerField(default=1)

class AtMessage(models.Model):
    member = models.ForeignKey('UserApi.UserInfo', on_delete=models.CASCADE)
    team = models.ForeignKey('Team', on_delete=models.CASCADE)
    teamMessage = models.ForeignKey('TeamMessage', on_delete=models.CASCADE)


class UnreadMessage(models.Model):
    member = models.ForeignKey('UserApi.UserInfo', on_delete=models.CASCADE)
    team = models.ForeignKey('Team', on_delete=models.CASCADE)
    nums = models.IntegerField(default=1)