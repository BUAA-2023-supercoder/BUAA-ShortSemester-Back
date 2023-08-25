import json
import os

from django.http import JsonResponse
from django.utils.crypto import get_random_string

from summer_web.urls import URL
from .models import Team, TeamMember, TYPE_ITEM, ROLE_ITEM, TeamMessage
from UserApi.models import UserInfo, GENDER_ITEMS
from UserApi.admin import validateAccessToken, getUserFromToken


# Create your views here.
def createTeam(request):
    if request.method != "POST":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)

    data = json.loads(request.body)
    accessToken = request.headers.get('Authorization').split(' ')[1]
    if validateAccessToken(accessToken):
        member = UserInfo.objects.get(email=getUserFromToken(accessToken))
        name = data.get('name')
        team = Team.objects.create(creator=member, name=name)
        TeamMember.objects.create(member=member, teamID=team, role=0)
        return JsonResponse({'msg': 'success'}, status=200)
    else:
        JsonResponse({'message': 'please login first'}, status=400)

def setAdmin(request):
    if request.method != "POST":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)

    data = json.loads(request.body)
    accessToken = request.headers.get('Authorization').split(' ')[1]
    decodedToken = validateAccessToken(accessToken)
    teamId = data.get('teamID')
    email = data.get('email')
    new_role = data.get('perm')
    if decodedToken:
        try:
            team = Team.objects.get(id=teamId)
            user = UserInfo.objects.get(email=email)
            ordinaryMember = TeamMember.objects.get(member=user, teamID=team)
            admin = UserInfo.objects.get(email=getUserFromToken(accessToken))
            team_member = TeamMember.objects.get(member=admin, teamID=team)
            role = team_member.role
            # 管理员不能将成员的身份设置为普通成员
            if role == 1 and new_role == 2:
                return JsonResponse({'msg': 'fail', 'error': 'insufficient member permissions'}, status=400)
            # 普通成员不能操作此功能
            if role == 2:
                return JsonResponse({'msg': 'fail', 'error': 'insufficient member permissions'}, status=400)
            if new_role == 0:
                return JsonResponse({'msg': 'fail', 'error': 'can not be set as creator'}, status=400)
            TeamMember.objects.get(member=ordinaryMember, teamID=team).update(role=new_role)
            return JsonResponse({'msg': 'success'}, status=200)
        except UserInfo.DoesNotExist:
            return JsonResponse({'msg': 'fail', 'error': 'member does not exist'}, status=400)
        except Team.DoesNotExist:
            return JsonResponse({'msg': 'fail', 'error': 'team does not exist'}, status=400)


def setTeamProfile(request):
    if request.method != "POST":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)

    accessToken = request.headers.get('Authorization').split(' ')[1]
    if validateAccessToken(accessToken):
        data = request.POST
        team = Team.objects.get(id=data.get('teamID'))
        user = UserInfo.objects.get(email=getUserFromToken(accessToken))
        perm = TeamMember.objects.get(teamID=team, member=user)
        if perm is None or perm.role == 2:
            return JsonResponse({'msg': 'fail', 'error': 'insufficient member permissions'}, status=400)

        if team is None:
            return JsonResponse({'msg': 'fail', 'error': 'wrong teamID'}, status=400)
        img = request.FILES['img']
        if team.profile.url != '/media/TeamProfile/default.png':
            os.remove("." + team.profile.url)
        img.name = get_random_string(length=8) + ".jpg"
        team.profile = img
        team.save()
        return JsonResponse({'msg': 'success'}, status=200)
    else:
        return JsonResponse({'msg': 'fail', 'error': 'user does not exist'}, status=400)

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
            team_member = TeamMember.objects.get(member=inviter, teamID=team)
            role = team_member.role
            if role == 2:
                return JsonResponse({'msg': 'fail', 'error': 'insufficient member permissions'}, status=400)
            if team.teammember_set.filter(member=invitees).exists():
                return JsonResponse({'msg': 'fail', 'error': 'the member is already on the team'}, status=400)
            team_member = TeamMember.objects.create(member=invitees, teamID=team)
            return JsonResponse({'msg': 'success'}, status=200)
        except UserInfo.DoesNotExist:
            return JsonResponse({'msg': 'fail', 'error': 'member does not exist'}, status=400)
        except Team.DoesNotExist:
            return JsonResponse({'msg': 'fail', 'error': 'team does not exist'}, status=400)
    else:
        return JsonResponse({'msg': 'fail', 'error': 'please login first'}, status=400)

def removeMember(request):
    if request.method != "POST":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)

    data = json.loads(request.body)
    accessToken = request.headers.get('Authorization').split(' ')[1]
    decodedToken = validateAccessToken(accessToken)
    teamId = data.get('teamID')
    email = data.get('email')

    if decodedToken:
        try:
            remover = UserInfo.objects.get(email=getUserFromToken(accessToken))
            team = Team.objects.get(id=teamId)  # 团队
            member_to_remove = UserInfo.objects.get(email=email)  # 成员

            team_member = TeamMember.objects.get(member=remover, teamID=team)
            role = team_member.role
            #普通用户不能踢人^^
            if role == 2:
                return JsonResponse({'msg': 'fail', 'error': 'insufficient member permissions'}, status=400)
            #管理员只能踢普通成员
            if role == 1 and TeamMember.objects.get(member=member_to_remove, teamID=team).first().role != 2:
                return JsonResponse({'msg': 'fail', 'error': 'insufficient member permissions'}, status=400)
            if not team.teammember_set.filter(member=member_to_remove).exists():
                return JsonResponse({'msg': 'fail', 'error': 'the member is not on the team'}, status=400)
            if team.teammember_set.filter(member=member_to_remove, teamID=team).first().role != 2:
                return JsonResponse({'msg': 'fail', 'error': 'can only delete putong member'}, status=400)
            team.teammember_set.filter(member=member_to_remove).delete()
            return JsonResponse({'msg': 'success'}, status=200)
        except UserInfo.DoesNotExist:
            return JsonResponse({'msg': 'fail', 'error': 'this member does not exist'}, status=400)
        except Team.DoesNotExist:
            return JsonResponse({'msg': 'fail', 'error': 'this team does not exist'}, status=400)
    else:
        return JsonResponse({'msg': 'fail', 'error': 'please login first'}, status=400)


def getAllTeam(request):
    if request.method != "POST":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)

    accessToken = request.headers.get('Authorization').split(' ')[1]
    if validateAccessToken(accessToken):
        user = UserInfo.objects.get(email=getUserFromToken(accessToken))
        res = TeamMember.objects.filter(member=user)
        result = list()
        for item in res:
            team = {
                "teamID": item.teamID.id,
                "name": item.teamID.name,
                'teamProfile': URL + item.teamID.profile.url
            }
            result.append(team)
        return JsonResponse({'msg': 'success', 'result': result}, status=200)
    else:
        return JsonResponse({'msg': 'fail', 'error': 'please login first'}, status=400)


def getAllMember(request):
    if request.method != "POST":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)

    accessToken = request.headers.get('Authorization').split(' ')[1]
    if validateAccessToken(accessToken):
        teamID = json.loads(request.body).get('teamID')
        res = TeamMember.objects.order_by('role').filter(teamID=teamID)
        result = list()
        for item in res:
            member = {
                "email": item.member.email,
                "gender": GENDER_ITEMS[item.member.gender][1],
                "nickname": item.member.nickname,
                "realname": item.member.realname,
                "role": ROLE_ITEM[item.role][1],
                "profile": URL + item.member.profile.url
            }
            result.append(member)
        return JsonResponse({'msg': 'success', 'result': result}, status=200)
    else:
        return JsonResponse({'msg': 'fail', 'error': 'please login first'}, status=400)

def addMessage(request):
    if request.method != "POST":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)

    accessToken = request.headers.get('Authorization').split(' ')[1]
    if validateAccessToken(accessToken):
        data = request.POST
        team = Team.objects.get(id=data.get('teamID'))
        sender = UserInfo.objects.get(email=getUserFromToken(accessToken))
        type = data.get('type')
        newMsg = TeamMessage.objects.create(sender=sender, team=team, type=0)
        strAfter = None
        if type == 'text':
            if data.get('text') is None:
                newMsg.delete()
                return JsonResponse({'msg': 'fail', 'error': 'text is None'}, status=400)
            newMsg.text = data.get('text')
            strAfter = data.get('text')
        elif type == 'image':
            if request.FILES['img'] is None:
                newMsg.delete()
                return JsonResponse({'msg': 'fail', 'error': 'image is None'}, status=400)
            newMsg.type = 1
            image = request.FILES['img']
            image.name = get_random_string(length=8) + ".jpg"
            newMsg.image = image
            strAfter = 'xxxxxx'
        elif type == 'file':
            if request.FILES['file'] is None:
                newMsg.delete()
                return JsonResponse({'msg': 'fail', 'error': 'file is None'}, status=400)
            newMsg.type = 2
            newMsg.file = request.FILES['file']
            newMsg.fileName = request.FILES['file'].name
        else:
            newMsg.delete()
            return JsonResponse({'msg': 'fail', 'error': 'wrong message type'}, status=400)
        newMsg.save()
        return JsonResponse({'msg': 'success'}, status=200)
    else:
        return JsonResponse({'msg': 'fail', 'error': 'please login first'}, status=400)
