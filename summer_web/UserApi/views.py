import json
import os
import platform
import random
import string

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.shortcuts import render
from django.template import loader
from rest_framework_simplejwt.tokens import RefreshToken

from UserApi.models import UserInfo
from summer_web.settings import EMAIL_HOST_USER


def sendEmail(request):
    if request.method != "POST":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)
    data = json.loads(request.body)
    email = data.get('email')
    if email is None:
        return JsonResponse({'msg': 'fail', 'error': 'wrong post parameter'}, status=500)
    email_title = None
    email_body = None
    # if platform.system() == "Linux":
    #     url = os.path.join("http://154.8.183.51/user/sending/", string)
    # else:
    #     url = os.path.join("http://127.0.0.1:8888/user/sending/", string)
    verify = ''
    list1 = []
    c = random.randint(0, 3)  # 生成随机数c，值随机为0-3
    for i in range(0, 5):  # 重复运行四次
        if c == i:  # 如果c=i,输出数字
            list1.append(random.randint(0, 9))
        else:  # 如果c!=i,输出字母
            list1.append(chr(random.randint(65, 90)))  # chr函数：将对应数字转为对应ascll码
    for i in list1:  # 将列表转为字符串
        verify += str(i)
    email_title = r"账号注册"
    email_body = loader.render_to_string('email_register.html', {'email': email, 'verify': verify})
    try:
        msg = EmailMessage(email_title, email_body, EMAIL_HOST_USER, [email])
        msg.content_subtype = 'html'
        send_status = msg.send()
        if send_status == 1:
            request.session['verify'] = verify
            request.session.set_expiry(60 * 60 * 24)
            return JsonResponse({'msg': 'success'}, status=200)
        else:
            return JsonResponse({'msg': 'fail', 'error': 'email send wrong'}, status=500)
    except Exception as e:
        return JsonResponse({'msg': 'fail', 'error': 'email send wrong'}, status=500)


# Create your views here.
def register(request):
    if request.method != "POST":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)
    data = json.loads(request.body)
    email = data.get('email')
    nickname = data.get('nickname')
    realname = data.get('realname')
    password = data.get('password')
    verify = data.get('verify')
    if email is None or realname is None or password is None or nickname is None or verify is None:
        return JsonResponse({'msg': 'fail', 'error': 'wrong post parameter'}, status=500)
    if request.session['verify'] is None or verify.upper() != request.session['verify']:
        return JsonResponse({'msg': 'fail', 'error': 'wrong verify'}, status=500)
    cnt = UserInfo.objects.filter(email=email).count()
    if cnt != 0:
        return JsonResponse({'msg': 'fail', 'error': 'email exists'}, status=403)
    request.session['verify'] = None
    user = User.objects.create_user(username=email, password=password)
    UserInfo.objects.create(email=email, password=password, nickname=nickname, realname=realname, user=user)
    return JsonResponse({'msg': 'success'}, status=200)


def login(request):
    if request.method != "POST":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)
    data = json.loads(request.body)
    email = data.get('email')
    password = data.get('password')
    if email is None or password is None:
        return JsonResponse({'msg': 'fail', 'error': 'wrong post parameter'}, status=500)
    user = authenticate(request, username=email, password=password)
    if user is not None:
        refresh = RefreshToken.for_user(user)
        accessToken = refresh.access_token
        responseData = {
            'refresh': str(refresh),
            'access': str(accessToken),
            'msg': 'success'
        }
        return JsonResponse(responseData, status=200)
    else:
        return JsonResponse({'msg': 'login fail'}, status=400)
