import json
import os
import re
from django.db.models import Q
from django.http import JsonResponse
from django.utils.crypto import get_random_string

from summer_web.urls import URL
from .models import Team, TeamMember, TYPE_ITEM, ROLE_ITEM, TeamMessage, AtMessage, UnreadMessage, SingleUnread
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
        JsonResponse({'message': 'fail', 'error': 'please login first'}, status=400)


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
            ordinaryMember.role = new_role
            ordinaryMember.save()
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
            inviter = UserInfo.objects.get(email=getUserFromToken(accessToken))  # user
            team = Team.objects.get(id=teamId)  # team
            invitees = UserInfo.objects.get(email=email)  # user
            team_member = TeamMember.objects.get(member=inviter, teamID=team)
            role = team_member.role
            if role == 2:
                return JsonResponse({'msg': 'fail', 'error': 'insufficient member permissions'}, status=400)
            if team.teammember_set.filter(member=invitees).exists():
                return JsonResponse({'msg': 'fail', 'error': 'the member is already on the team'}, status=200)
            team_member = TeamMember.objects.create(member=invitees, teamID=team)
            return JsonResponse({'msg': 'success'}, status=200)
        except UserInfo.DoesNotExist:
            return JsonResponse({'msg': 'fail', 'error': 'member does not exist'}, status=200)
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
            # 普通用户不能踢人^^
            if role == 2:
                return JsonResponse({'msg': 'fail', 'error': 'insufficient member permissions'}, status=400)

            # 创建者可以踢全部成员
            if role == 0:
                if not team.teammember_set.filter(member=member_to_remove).exists():
                    return JsonResponse({'msg': 'fail', 'error': 'the member is not on the team'}, status=400)
                if remover == member_to_remove:
                    return JsonResponse({'msg': 'fail', 'error': 'cannot remove yourself'}, status=400)
                team.teammember_set.filter(member=member_to_remove).delete()
                return JsonResponse({'msg': 'success'}, status=200)

            # 管理员只能踢普通成员
            if role == 1 and TeamMember.objects.get(member=member_to_remove, teamID=team).first().role != 2:
                return JsonResponse({'msg': 'fail', 'error': 'insufficient member permissions'}, status=400)
            if not team.teammember_set.filter(member=member_to_remove).exists():
                return JsonResponse({'msg': 'fail', 'error': 'the member is not on the team'}, status=400)
            if team.teammember_set.filter(member=member_to_remove, teamID=team).first().role != 2:
                return JsonResponse({'msg': 'fail', 'error': 'can only delete normal member'}, status=400)
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


def getAllFriends(request):
    if request.method != "POST":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)

    accessToken = request.headers.get('Authorization').split(' ')[1]
    if validateAccessToken(accessToken):
        user = UserInfo.objects.get(email=getUserFromToken(accessToken))
        relation = TeamMember.objects.filter(member=user)
        teams = list()
        for item in relation:
            teams.append(item.teamID)
        colleague = TeamMember.objects.filter(teamID__in=teams)
        result = dict()
        for item in colleague:
            person = item.member
            if person == user:
                continue
            if person.email not in result:
                info = {
                    'nickname': person.nickname,
                    'realname': person.realname,
                    'profile': URL + person.profile.url,
                    'teams': [{'teamID': item.teamID.id, 'name': item.teamID.name}]
                }
                result[person.email] = info
            else:
                result[person.email]['teams'].append({'teamID': item.teamID.id, 'name': item.teamID.name})
        return JsonResponse({'msg': 'success', 'colleague': result}, status=200)
    else:
        return JsonResponse({'msg': 'fail', 'error': 'please login first'}, status=400)


def saveUnread(sender, team):
    persons = TeamMember.objects.filter(teamID=team)
    for person in persons:
        if person.member != sender:
            if UnreadMessage.objects.filter(team=team, member=person.member).count() == 0:
                UnreadMessage.objects.create(team=team, member=person.member)
            else:
                obj = UnreadMessage.objects.get(team=team, member=person.member)
                obj.nums = obj.nums + 1
                obj.save()
        else:
            if UnreadMessage.objects.filter(team=team, member=person.member).count() != 0:
                UnreadMessage.objects.get(team=team, member=person.member).delete()
    return


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
            text = data.get('text')
            newMsg.text = text
            strAfter = data.get('text') + '@$%' + str(newMsg.id)
            if '@' in text:  # 检查 @ 后面是否跟着邮箱
                email_list = re.findall(r'@([^\s]+)\s', text)
                for email in email_list:
                    member = UserInfo.objects.get(email=email)
                    if TeamMember.objects.filter(member=member, teamID=team).count() != 0:  # 艾特的这个人必须在这个团队里面
                        if AtMessage.objects.filter(teamMessage=newMsg, team=team, member=member).count() == 0:
                            AtMessage.objects.create(member=member, team=team, teamMessage=newMsg)
        elif type == 'forwardmessage':

            if data.get('text') is None:
                newMsg.delete()
                return JsonResponse({'msg': 'fail', 'error': 'text is None'}, status=400)
            text = data.get('text')
            newMsg.text = text
            newMsg.type = 3
            strAfter = data.get('text') + '@$%' + str(newMsg.id)

        elif type == 'image':

            if request.FILES['img'] is None:
                newMsg.delete()
                return JsonResponse({'msg': 'fail', 'error': 'image is None'}, status=400)
            newMsg.type = 1
            image = request.FILES['img']
            image.name = get_random_string(length=8) + ".jpg"
            newMsg.image = image
            strAfter = '$$$' + 'Images' + '$$$' + image.name + '@$%' + str(newMsg.id)
        elif type == 'file':
            if request.FILES['file'] is None:
                newMsg.delete()
                return JsonResponse({'msg': 'fail', 'error': 'file is None'}, status=400)
            newMsg.type = 2
            newMsg.file = request.FILES['file']
            newMsg.fileName = newMsg.file.name
            strAfter = '$$$' + 'Files' + '$$$' + newMsg.fileName + '@$%' + str(newMsg.id)
        else:
            newMsg.delete()
            return JsonResponse({'msg': 'fail', 'error': 'wrong message type'}, status=400)
        newMsg.save()
        saveUnread(sender, team)
        return JsonResponse({'msg': 'success', 'str': strAfter, 'ID': newMsg.id}, status=200)
    else:
        return JsonResponse({'msg': 'fail', 'error': 'please login first'}, status=400)


def messageAt(request):
    if request.method != "POST":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)

    accessToken = request.headers.get('Authorization').split(' ')[1]
    if validateAccessToken(accessToken):
        data = json.loads(request.body)
        member = UserInfo.objects.get(email=data.get('email'))
        team = Team.objects.get(id=data.get('teamID'))
        message = TeamMessage.objects.get(id=data.get('msgID'))
        if member is None or team is None or message is None or team != message.team:
            return JsonResponse({'msg': ' fail', 'error': 'wrong info'}, status=400)
        if AtMessage.objects.filter(teamMessage=message, team=team, member=member).count() == 0:
            AtMessage.objects.create(member=member, team=team, teamMessage=message)
        return JsonResponse({'msg': 'success'}, status=200)
    else:
        return JsonResponse({'msg': 'fail', 'error': 'please login first'}, status=400)


def getAtMessage(request):
    if request.method != "POST":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)

    accessToken = request.headers.get('Authorization').split(' ')[1]
    if validateAccessToken(accessToken):
        user = UserInfo.objects.get(email=getUserFromToken(accessToken))
        res = AtMessage.objects.order_by('teamMessage__time').filter(member=user)
        result = list()
        for item in res:
            info = {
                'ID': item.teamMessage.id,
                'teamID': item.team.id,
                'teamName': item.team.name,
                'text': item.teamMessage.text,
                'time': item.teamMessage.time.strftime("%Y-%m-%d %H:%M:%S"),
                'who': {
                    'email': item.teamMessage.sender.email,
                    'profile': URL + item.teamMessage.sender.profile.url,
                    'nickname': item.teamMessage.sender.nickname,
                    'realname': item.teamMessage.sender.realname
                }
            }
            result.append(info)
        return JsonResponse({'msg': 'success', 'result': result}, status=200)
    else:
        return JsonResponse({'msg': 'fail', 'error': 'please login first'}, status=400)


def skipToAtPosition(request):  # not test
    if request.method != "POST":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)

    accessToken = request.headers.get('Authorization').split(' ')[1]
    if validateAccessToken(accessToken):
        user = UserInfo.objects.get(email=getUserFromToken(accessToken))
        atID = json.loads(request.body).get('ID')
        atMessage = AtMessage.objects.get(id=atID)
        if atMessage.member != user:
            return JsonResponse({'msg': 'fail', 'error': 'information error, please check your database'}, status=400)
        time = atMessage.teamMessage.time
        msg = TeamMessage.objects.filter(Q(team=atMessage.team) & Q(time__gte=time)).order_by('time')
        msgList = list()
        for item in msg:
            message = item.text
            if item.type == 1:
                message = URL + item.image.url
            elif item.type == 2:
                message = URL + item.file.url
            info = {
                'sender': {
                    'email': item.sender.email,
                    'profile': URL + item.sender.profile.url,
                    'nickname': item.sender.nickname,
                    'realname': item.sender.realname
                },
                'teamID': item.team.id,
                'messageID': item.id,
                'time': item.time.strftime("%Y-%m-%d %H:%M:%S"),
                'type': item.type,
                'message': message
            }
            msgList.append(info)
        if UnreadMessage.objects.filter(team=atMessage.team, member=user).count() != 0:
            UnreadMessage.objects.get(team=atMessage.team, member=user).delete()
        return JsonResponse({'msg': 'success', 'chatHistory': msgList}, status=200)
    else:
        return JsonResponse({'msg': 'fail', 'error': 'please login first'}, status=400)


def getLateHistory(request):
    if request.method != "POST":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)

    accessToken = request.headers.get('Authorization').split(' ')[1]
    if validateAccessToken(accessToken):
        teamID = json.loads(request.body).get('teamID')
        times = json.loads(request.body).get('times')
        team = Team.objects.get(id=teamID)
        if times is None:
            times = 50
        print(times)
        if team is None:
            return JsonResponse({'msg': 'fail', 'error': 'teamID does not exist'}, status=400)
        records = list(TeamMessage.objects.filter(team=team).order_by('time'))
        result = list()
        for idx in range(max(0, len(records) - times), len(records)):
            item = records[idx]
            message = item.text
            if item.type == 1:
                message = URL + item.image.url
            elif item.type == 2:
                message = URL + item.file.url
            info = {
                'sender': {
                    'email': item.sender.email,
                    'profile': URL + item.sender.profile.url,
                    'nickname': item.sender.nickname,
                    'realname': item.sender.realname
                },
                'teamID': item.team.id,
                'messageID': item.id,
                'time': item.time.strftime("%Y-%m-%d %H:%M:%S"),
                'type': item.type,
                'message': message
            }
            result.append(info)
        user = UserInfo.objects.get(email=getUserFromToken(accessToken))
        if UnreadMessage.objects.filter(team=team, member=user).count() != 0:
            UnreadMessage.objects.get(team=team, member=user).delete()
        return JsonResponse({'msg': 'success', 'chatHistory': result}, status=200)
    else:
        return JsonResponse({'msg': 'fail', 'error': 'please login first'}, status=400)


def getHistory(request):
    if request.method != "POST":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)

    accessToken = request.headers.get('Authorization').split(' ')[1]
    if validateAccessToken(accessToken):
        ID = json.loads(request.body).get('ID')
        endMessage = TeamMessage.objects.get(id=ID)
        if endMessage is None:
            return JsonResponse({'msg': 'fail', 'error': 'messageID wrong'}, status=400)
        earlier = TeamMessage.objects.filter(Q(team=endMessage.team) & Q(time__lt=endMessage.time)).order_by('time')
        sz = len(earlier)
        earlier = list(earlier)
        result = list()
        begin = max(0, sz - 50)
        for idx in range(begin, sz):
            item = earlier[idx]
            message = item.text
            if item.type == 1:
                message = URL + item.image.url
            elif item.type == 2:
                message = URL + item.file.url
            info = {
                'sender': {
                    'email': item.sender.email,
                    'profile': URL + item.sender.profile.url,
                    'nickname': item.sender.nickname,
                    'realname': item.sender.realname
                },
                'teamID': item.team.id,
                'messageID': item.id,
                'time': item.time.strftime("%Y-%m-%d %H:%M:%S"),
                'type': item.type,
                'message': message
            }
            result.append(info)
        user = UserInfo.objects.get(email=getUserFromToken(accessToken))
        if UnreadMessage.objects.filter(team=endMessage.team, member=user).count() != 0:
            UnreadMessage.objects.get(team=endMessage.team, member=user).delete()
        return JsonResponse({'msg': 'success', 'chatHistory': result}, status=200)
    else:
        return JsonResponse({'msg': 'fail', 'error': 'please login first'}, status=400)


def deleteAtMsg(request):
    if request.method != "POST":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)

    accessToken = request.headers.get('Authorization').split(' ')[1]
    if validateAccessToken(accessToken):
        ID = json.loads(request.body).get('ID')
        user = UserInfo.objects.get(email=getUserFromToken(accessToken))
        atMsg = AtMessage.objects.get(id=ID)
        if user != atMsg.member:
            return JsonResponse({'msg': 'fail', 'error': 'that record is not yours'}, status=400)
        if atMsg is None:
            return JsonResponse({'msg': 'fail', 'error': 'ID does not exist'}, status=400)
        atMsg.delete()
        return JsonResponse({'msg': 'success'}, status=200)
    else:
        return JsonResponse({'msg': 'fail', 'error': 'please login first'}, status=400)


def getUnreadInfo(request):
    if request.method != "POST":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)

    accessToken = request.headers.get('Authorization').split(' ')[1]
    if validateAccessToken(accessToken):
        user = UserInfo.objects.get(email=getUserFromToken(accessToken))
        result = UnreadMessage.objects.filter(member=user)
        teamInfo = list()
        totNum = 0
        for item in result:
            info = {
                'teamID': item.team.id,
                'name': item.team.name,
                'nums': item.nums
            }
            totNum = totNum + item.nums
            teamInfo.append(info)

        singleRecord = SingleUnread.objects.filter(host=user)
        singleInfo = list()
        for item in singleRecord:
            info = {
                'email': item.host.email,
                'nums': item.cnt
            }
            totNum = totNum + item.cnt
            singleInfo.append(info)
        return JsonResponse({'msg': 'success', 'teamInfo': teamInfo,
                             'singleInfo': singleInfo, 'tot': totNum}, status=200)
    else:
        return JsonResponse({'msg': 'fail', 'error': 'please login first'}, status=400)


def readAtMessage(request):
    if request.method != "POST":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)

    accessToken = request.headers.get('Authorization').split(' ')[1]
    if validateAccessToken(accessToken):
        msgID = json.loads(request.body).get('messageID')
        msg = TeamMessage.objects.get(id=msgID)
        user = UserInfo.objects.get(email=getUserFromToken(accessToken))
        AtMessage.objects.get(member=user, teamMessage=msg).delete()
        return JsonResponse({'mag': 'success'}, status=200)
    else:
        return JsonResponse({'msg': 'fail', 'error': 'please login first'}, status=400)


def accessTeamChat(request):
    if request.method != "POST":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)

    accessToken = request.headers.get('Authorization').split(' ')[1]
    if validateAccessToken(accessToken):
        teamID = json.loads(request.body).get('teamID')
        team = Team.objects.get(id=teamID)
        user = UserInfo.objects.get(email=getUserFromToken(accessToken))
        obj = AtMessage.objects.get(member=user, team=team)
        if obj is not None:
            obj.delete()
        obj = UnreadMessage.objects.get(member=user, team=team)
        if obj is not None:
            obj.delete()
        return JsonResponse({'msg': 'success'}, status=200)
    else:
        return JsonResponse({'msg': 'fail', 'error': 'please login first'}, status=400)
