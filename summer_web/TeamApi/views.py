import json

from django.http import JsonResponse
from django.shortcuts import render
from .models import Team, TeamMember
from UserApi.models import UserInfo
from django.contrib.auth.models import User
from summer_web import UserApi
from .admin import validateAccessToken, getUserFromToken


# Create your views here.
def createTeam(request):
    if request.method != "POST":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)

    data = json.loads(request.body)
    member = UserInfo.objects.get(email=data.get('email'))
    name = data.get('name')
    try:
        team = Team.objects.create(creator=member, name=name)
        TeamMember.objects.create(member=member, teamID=team, role=0)
        return JsonResponse({'msg': 'success'}, status=200)
    except Exception as e:
        return JsonResponse({'msg': 'fail', 'error': str(e)}, status=500)
def setAdmin(request):
    if request.method!="POST":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)
    data=json.loads(request.body)

def invite(request):
    if request.method!="POST":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)
    data=json.loads(request.body)
    accessToken = request.headers.get('Authorization').split(' ')[1]
    decodedToken = validateAccessToken(accessToken)
    teamId=data.get['teamId']
    email=data.get['email']
    if decodedToken:
        try:
            inviter=getUserFromToken(accessToken) #user
            team=Team.objects.get(id=teamId) #team
            invitees=User.objects.get(email=email) #user
            #判断邀请者的权限
            team_member = TeamMember.objects.get(member=inviter,teamID=team)
            role = team_member.role
            if role==2:
                return JsonResponse({'message': '成员权限不足'}, status=400)
            # 判断成员是否已经是团队的成员
            if team.teammember_set.filter(member=invitees).exists():
                return JsonResponse({'message': '该成员已经是团队的成员'}, status=400)
            # 创建 TeamMember 对象将成员加入团队
            team_member = TeamMember.objects.create(member=invitees, teamID=team)
            return JsonResponse({'message': '成员成功加入团队'}, status=200)
        except UserApi.UserInfo.DoesNotExist:
            return JsonResponse({'message': '成员不存在'}, status=400)
        except Team.DoesNotExist:
            return JsonResponse({'message': '团队不存在'}, status=400)
    else:
        return JsonResponse({'message': 'please login first'})