import json

from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.shortcuts import render

from UserApi.models import UserInfo


# Create your views here.
def register(request):
    data = json.loads(request.body)
    email = data.get('email')
    cnt = UserInfo.objects.filter(email=email).count()
    if cnt != 0:
        return JsonResponse({'msg': 'fail', 'error': 'email exists'}, status=403)
    # send Email
    return JsonResponse({'msg': 'success'}, status=200)

def login(request):
    data = json.loads(request.body)
    email = data.get('email')
    password = data.get('password')
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
        return JsonResponse({'msg': 'fail'}, status=400)


