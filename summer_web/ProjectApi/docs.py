import json
import random
from django.http import JsonResponse

from ProjectApi.models import Project, PrototypePage, Document
from TeamApi.models import Team, TeamMember
from UserApi.models import UserInfo
from summer_web.admin import getUserFromToken
from UserApi.admin import validateAccessToken, getUserFromToken
from summer_web.urls import URL

def saveDoc(request):
    if request.method != "POST":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)

    accessToken = request.headers.get('Authorization').split(' ')[1]
    if validateAccessToken(accessToken):
        print('666')
    else:
        return JsonResponse({'msg': 'fail', 'error': 'user does not exist'}, status=400)