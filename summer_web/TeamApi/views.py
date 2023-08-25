import json

from django.http import JsonResponse
from .models import Team, TeamMember, TYPE_ITEM, ROLE_ITEM, TeamMessage
from UserApi.models import UserInfo, GENDER_ITEMS
from UserApi.admin import validateAccessToken, getUserFromToken


# Create your views here.
def createTeam(request):
    if request.method != "POST":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)

    data = json.loads(request.body)
    member = UserInfo.objects.get(email=data.get('email'))
    name = data.get('name')
    accessToken = request.headers.get('Authorization').split(' ')[1]
    if validateAccessToken(accessToken):
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
            ordinarymember = TeamMember.objects.get(member=user, teamID=team)
            admin = UserInfo.objects.get(email=getUserFromToken(accessToken))
            team_member = TeamMember.objects.get(member=admin, teamID=team)
            role = team_member.role
            if role == 2:
                return JsonResponse({'msg': 'fail', 'error': 'insufficient member permissions'}, status=400)
            if new_role == 0:
                return JsonResponse({'msg': 'fail', 'error': 'can not be set as creator'}, status=400)
            TeamMember.objects.get(member=ordinarymember, teamID=team).update(role=new_role)
            return JsonResponse({'msg': 'success'}, status=200)
        except UserInfo.DoesNotExist:
            return JsonResponse({'msg': 'fail', 'error': 'member does not exist'}, status=400)
        except Team.DoesNotExist:
            return JsonResponse({'msg': 'fail', 'error': 'team does not exist'}, status=400)


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
            if role == 2:
                return JsonResponse({'msg': 'fail', 'error': 'insufficient member permissions'}, status=400)

            if not team.teammember_set.filter(member=member_to_remove).exists():
                return JsonResponse({'msg': 'fail', 'error': 'the member is not on the team'}, status=400)
            if team.teammember_set.filter(member=member_to_remove,teamID=team).first().role != 2:
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
                "name": item.teamID.name
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
                "role": ROLE_ITEM[item.role][1]
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
        if type == 'text':
            if data.get('text') is None:
                newMsg.delete()
                return JsonResponse({'msg': 'fail', 'error': 'text is None'}, status=400)
            newMsg.text = data.get('text')
        elif type == 'image':
            if request.FILES['img'] is None:
                newMsg.delete()
                return JsonResponse({'msg': 'fail', 'error': 'image is None'}, status=400)
            newMsg.type = 1
            newMsg.image = request.FILES['img']
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
