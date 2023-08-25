import json

from django.http import JsonResponse
from django.shortcuts import render
from .models import Team, TeamMember
from UserApi.models import UserInfo
from django.contrib.auth.models import User

from UserApi.admin import validateAccessToken, getUserFromToken


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
    if request.method != "POST":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)
    data = json.loads(request.body)
    accessToken = request.headers.get('Authorization').split(' ')[1]
    decodedToken = validateAccessToken(accessToken)
    teamId = data.get('teamID')
    email = data.get('email')
    newrole=data.get('role')
    if decodedToken:
        try:
            team = Team.objects.get(id=teamId)  # team
            user = UserInfo.objects.get(email=email)  # user
            ordinarymember = TeamMember.objects.get(member=user, teamID=team)
            admin = UserInfo.objects.get(email=getUserFromToken(accessToken))  # user
            #判断管理员是否有管理权限
            # 判断邀请者的权限

            team_member = TeamMember.objects.get(member=admin, teamID=team)
            role = team_member.role
            if role == 2:
                return JsonResponse({'msg': '成员权限不足'}, status=400)

            ordinarymember.role = newrole
            ordinarymember.save()

            return JsonResponse({'msg': 'success'}, status=200)
        except UserInfo.DoesNotExist:
            return JsonResponse({'msg': '成员不存在'}, status=400)
        except Team.DoesNotExist:
            return JsonResponse({'msg': '团队不存在'}, status=400)
def invite(request):
    if request.method != "POST":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)

    data = json.loads(request.body)
    accessToken = request.headers.get('Authorization').split(' ')[1]
    decodedToken = validateAccessToken(accessToken)
    teamId = data.get('teamID')
    email = data.get('email')
    if decodedToken:
        try:
            inviter = UserInfo.objects.get(email=getUserFromToken(accessToken))     # user
            team = Team.objects.get(id=teamId)  # team
            invitees = UserInfo.objects.get(email=email)    # user
            # 判断邀请者的权限
            team_member = TeamMember.objects.get(member=inviter, teamID=team)
            role = team_member.role
            if role == 2:
                return JsonResponse({'msg': '成员权限不足'}, status=400)
            # 判断成员是否已经是团队的成员
            if team.teammember_set.filter(member=invitees).exists():
                return JsonResponse({'msg': '该成员已经是团队的成员'}, status=400)
            # 创建 TeamMember 对象将成员加入团队
            team_member = TeamMember.objects.create(member=invitees, teamID=team)
            return JsonResponse({'msg': '成员成功加入团队'}, status=200)
        except UserInfo.DoesNotExist:
            return JsonResponse({'msg': '成员不存在'}, status=400)
        except Team.DoesNotExist:
            return JsonResponse({'msg': '团队不存在'}, status=400)
    else:
        return JsonResponse({'msg': 'please login first'})


def remove_member(request):
    if request.method != "POST":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)

    data = json.loads(request.body)
    accessToken = request.headers.get('Authorization').split(' ')[1]
    decodedToken = validateAccessToken(accessToken)
    teamId = data.get('teamID')
    email = data.get('email')

    if decodedToken:
        try:
            remover = UserInfo.objects.get(email=getUserFromToken(accessToken))  # 用户
            team = Team.objects.get(id=teamId)  # 团队
            member_to_remove = UserInfo.objects.get(email=email)  # 成员

            team_member = TeamMember.objects.get(member=remover, teamID=team)
            role = team_member.role
            if role == 2:
                return JsonResponse({'msg': '成员权限不足'}, status=400)

            if not team.teammember_set.filter(member=member_to_remove).exists():
                return JsonResponse({'msg': '该成员不是团队的成员'}, status=400)
            if team.teammember_set.filter(member=member_to_remove,teamID=team).first().role!=2:
                return JsonResponse({'msg': '只可删除普通成员'}, status=400)
            team.teammember_set.filter(member=member_to_remove).delete()
            return JsonResponse({'msg': '成功从团队中删除成员'}, status=200)
        except UserInfo.DoesNotExist:
            return JsonResponse({'msg': '成员不存在'}, status=400)
        except Team.DoesNotExist:
            return JsonResponse({'msg': '团队不存在'}, status=400)
    else:
        return JsonResponse({'msg': 'please login first'})
