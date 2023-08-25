import json

from django.http import JsonResponse
from django.shortcuts import render

from ProjectApi.models import Project
from TeamApi.models import Team, TeamMember
from UserApi.models import UserInfo
from summer_web.admin import notAnonymous, getUserFromToken


def getProjectList(request):
    if request.method != "GET":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)
    if notAnonymous(request) is False:
        return JsonResponse({'msg': 'fail', 'error': 'login first please'}, status=401)
    data = json.loads(request.body)
    team = Team.objects.filter(id=data.get('teamId'))
    if not team:
        return JsonResponse({'msg': 'fail', 'error': 'team not exits'}, status=404)
    # 判断用户是否在该team中
    user = getUserFromToken(request.headers.get('Authorization').split(' ')[1])
    userInfo = UserInfo.objects.filter(user=user)
    if not TeamMember.objects.filter(teamID=team, member=userInfo):
        return JsonResponse({'msg': 'fail', 'error': 'user not in the team'}, status=404)
    projects = Project.objects.filter(team=team).values('id', 'projectName')
    return JsonResponse({'projects': list(projects)})


# Create your views here.
def createProject(request):
    if request.method != "POST":
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
        project = Project.objects.create(team=team, projectName=data.get('projectName'))
        return JsonResponse({'msg': 'success'}, status=200)
    except Exception as e:
        return JsonResponse({'msg': 'fail', 'error': str(e)}, status=500)


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
