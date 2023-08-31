import json
import os
import re
from django.db.models import Q
from django.http import JsonResponse
from django.utils.crypto import get_random_string

from summer_web.urls import URL
from .models import Team, TeamMember, TYPE_ITEM, ROLE_ITEM, TeamMessage, AtMessage, UnreadMessage
from UserApi.models import UserInfo, GENDER_ITEMS
from UserApi.admin import validateAccessToken, getUserFromToken

def createChatGroup(request):
    if request.method != "POST":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)

    data = json.loads(request.body)
    accessToken = request.headers.get('Authorization').split(' ')[1]
    if validateAccessToken(accessToken):
        member = UserInfo.objects.get(email=getUserFromToken(accessToken))
        name = data.get('name')
        team = Team.objects.create(creator=member, name=name, isReal=False)
        TeamMember.objects.create(member=member, teamID=team, role=0)
        return JsonResponse({'msg': 'success', 'chatGroupID': team.id}, status=200)
    else:
        JsonResponse({'message': 'fail', 'error': 'please login first'}, status=400)


def addToChatGroup(request):
    if request.method != "POST":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)

    data = json.loads(request.body)
    accessToken = request.headers.get('Authorization').split(' ')[1]
    if validateAccessToken(accessToken):
        email = data.get('email')
        ID = data.get('chatGroupID')
        chatGroup = Team.objects.get(id=ID)
        user = UserInfo.objects.get(email=getUserFromToken(accessToken))
        if chatGroup.creator != user:
            return JsonResponse({'msg': 'fail', 'error': 'you are not the group owner'}, status=205)
        member = UserInfo.objects.get(email=email)
        if member is None:
            return JsonResponse({'msg': 'fail', 'error': 'the member you want invite is not exist'}, status=204)
        TeamMember.objects.create(teamID=chatGroup, member=member)
        return JsonResponse({'msg': 'success'}, status=200)
    else:
        JsonResponse({'message': 'fail', 'error': 'please login first'}, status=400)


def delFromChatGroup(request):
    if request.method != "POST":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)

    accessToken = request.headers.get('Authorization').split(' ')[1]
    if validateAccessToken(accessToken):
        ID = json.loads(request.body).get('chatGroupID')
        user = UserInfo.objects.get(email=getUserFromToken(accessToken))
        chatGroup = Team.objects.get(id=ID)
        if chatGroup is None or chatGroup.isReal:
            return JsonResponse({'msg': 'fail', 'error': 'this group can not leave'}, status=205)
        if chatGroup.creator == user:
            return JsonResponse({'msg': 'fail', 'error': 'creator can not leave'}, status=205)
        TeamMember.objects.get(member=user, teamID=chatGroup).delete()
        return JsonResponse({'msg': 'success'}, status=200)
    else:
        JsonResponse({'message': 'fail', 'error': 'please login first'}, status=400)

def delTotalChatGroup(request):
    if request.method != "POST":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)

    accessToken = request.headers.get('Authorization').split(' ')[1]
    if validateAccessToken(accessToken):
        ID = json.loads(request.body).get('chatGroupID')
        user = UserInfo.objects.get(email=getUserFromToken(accessToken))
        chatGroup = Team.objects.get(id=ID)
        if chatGroup is None or chatGroup.isReal:
            return JsonResponse({'msg': 'fail', 'error': 'this group can not be deleted'}, status=400)
        if chatGroup.creator != user:
            return JsonResponse({'msg': 'fail', 'error': 'you are not the creator'}, status=400)
        chatGroup.delete()
        return JsonResponse({'msg': 'success'}, status=200)
    else:
        JsonResponse({'message': 'fail', 'error': 'please login first'}, status=400)