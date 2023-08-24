from django.db import models

GENDER_ITEMS = [
    (0, '未知直升机'),
    (1, '男'),
    (2, '女')
]

# Create your models here.
class User(models.Model):
    email = models.EmailField(primary_key=True, verbose_name="邮箱")
    nickname = models.CharField(max_length=128, null=False, verbose_name="昵称")
    realname = models.CharField(max_length=128, null=False, verbose_name="中文名字")
    password = models.CharField(max_length=128, null=False, verbose_name="密码")
    gender = models.IntegerField(choices=GENDER_ITEMS, default=0, verbose_name="性别")
