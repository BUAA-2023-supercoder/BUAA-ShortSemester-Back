import json
import random
from django.http import JsonResponse
from django.shortcuts import render

from ProjectApi.models import Project, PrototypePage
from TeamApi.models import Team, TeamMember
from UserApi.models import UserInfo
from summer_web.admin import notAnonymous, getUserFromToken
from UserApi.admin import validateAccessToken, getUserFromToken
from summer_web.urls import URL


def getProjectList(request):
    if request.method != "POST":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)

    accessToken = request.headers.get('Authorization').split(' ')[1]
    if validateAccessToken(accessToken):
        user = UserInfo.objects.get(email=getUserFromToken(accessToken))
        teamID = json.loads(request.body).get('teamID')
        team = list()
        if teamID is None:
            res = TeamMember.objects.filter(member=user)
            for item in res:
                team.append(item.teamID)
        else:
            team.append(Team.objects.get(id=teamID))
        Rye = list()
        projects = Project.objects.all().order_by('team_id')
        for item in projects:
            if item.team in team:
                info = {
                    'teamID': item.team.id,
                    'projectID': item.id,
                    'name': item.projectName,
                    'profile': URL + item.image.url
                }
                Rye.append(info)
        return JsonResponse({'msg': 'success', 'projects': Rye}, status=200)
    else:
        return JsonResponse({'msg': 'fail', 'error': 'user does not exist'}, status=400)


# Create your views here.
def createProject(request):
    if request.method != "POST":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)

    accessToken = request.headers.get('Authorization').split(' ')[1]
    if validateAccessToken(accessToken):
        data = json.loads(request.body)
        teamID = data.get('teamID')
        name = data.get('name')
        height = data.get('height')
        width = data.get('width')
        team = Team.objects.get(id=teamID)
        if team is None:
            return JsonResponse({'msg': 'fail', 'error': 'teamID does not exist'}, status=400)
        num = random.randint(1, 6)
        project = Project.objects.create(team=team,
                                         projectName=name if name is not None else 'untitled',
                                         profile='ProjectProfile/' + str(num) + '.jpg')
        page = PrototypePage.objects.create(project=project,
                                            prototypeName='untitled',
                                            context="",
                                            height=height,
                                            width=width)
        prototypePage = {
            'pageID': page.id,
            'name': page.prototypeName,
            'context': page.context,
            'height': page.length,
            'width': page.width
        }
        return JsonResponse({'msg': 'success', 'prototypePage': prototypePage}, status=200)
    else:
        return JsonResponse({'msg': 'fail', 'error': 'user does not exist'}, status=400)


def renameProject(request):
    if request.method != "PUT":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)
    data = json.loads(request.body)
    if notAnonymous(request) is False:
        return JsonResponse({'msg': 'fail', 'error': 'login first please'}, status=401)

    team = Team.objects.filter(id=data.get('teamId'))
    if not team:
        return JsonResponse({'msg': 'fail', 'error': 'team not exits'}, status=404)
    # 判断用户是否在该team中
    user = getUserFromToken(request.headers.get('Authorization').split(' ')[1])
    userInfo = UserInfo.objects.filter(user=user)
    if not TeamMember.objects.filter(teamID=team, member=userInfo):
        return JsonResponse({'msg': 'fail', 'error': 'user not in the team'}, status=404)
    try:
        cnt = Project.objects.filter(id=data.get('projectId')).update(projectName=data.get('projectName'))
        if not cnt:
            return JsonResponse({'msg': 'fail', 'error': 'wrong projectId'}, status=400)
        else:
            return JsonResponse({'msg': 'success'}, status=200)
    except Exception as e:
        return JsonResponse({'msg': 'fail', 'error': str(e)}, status=500)


def deleteProject(request):
    if request.method != "DELETE":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)
    data = json.loads(request.body)
    if notAnonymous(request) is False:
        return JsonResponse({'msg': 'fail', 'error': 'login first please'}, status=401)

    team = Team.objects.filter(id=data.get('teamId'))
    if not team:
        return JsonResponse({'msg': 'fail', 'error': 'team not exits'}, status=404)
    # 判断用户是否在该team中
    user = getUserFromToken(request.headers.get('Authorization').split(' ')[1])
    userInfo = UserInfo.objects.filter(user=user)
    if not TeamMember.objects.filter(teamID=team, member=userInfo):
        return JsonResponse({'msg': 'fail', 'error': 'user not in the team'}, status=404)
    try:
        cnt = Project.objects.filter(id=data.get('projectId')).update(isDelete=True)
        if not cnt:
            return JsonResponse({'msg': 'fail', 'error': 'wrong projectId'}, status=400)
        else:
            return JsonResponse({'msg': 'success'}, status=200)
    except Exception as e:
        return JsonResponse({'msg': 'fail', 'error': str(e)}, status=500)
