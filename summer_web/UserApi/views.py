import json
import os
import platform
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


def sendEmail(option, email):
    email_title = None
    email_body = None
    # if platform.system() == "Linux":
    #     url = os.path.join("http://154.8.183.51/user/sending/", string)
    # else:
    #     url = os.path.join("http://127.0.0.1:8888/user/sending/", string)
    if option == 0:
        email_title = r"账号注册"
        email_body = loader.render_to_string('email_register.html')
    elif option == 1:
        email_title = r"密码重置"
        email_body = loader.render_to_string('email_reset.html')
    try:
        msg = EmailMessage(email_title, email_body, EMAIL_HOST_USER, [email])
        msg.content_subtype = 'html'
        send_status = msg.send()
        print(send_status)
        return True
    except Exception as e:
        return False


# Create your views here.
def register(request):
    if request.method != "POST":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)
    data = json.loads(request.body)
    email = data.get('email')
    if email is None:
        return JsonResponse({'msg': 'fail', 'error': 'wrong post parameter'}, status=500)
    # password = data.get('password')
    cnt = UserInfo.objects.filter(email=email).count()
    if cnt != 0:
        return JsonResponse({'msg': 'fail', 'error': 'email exists'}, status=403)
    # send Email
    if sendEmail(0, email) is False:
        return JsonResponse({'msg': 'fail', 'error': 'email sending fails'}, status=500)
    # 下面代码用于测试
    # User.objects.create_user(username=email, password=password)
    # UserInfo.objects.create(email=email, password=password)
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
