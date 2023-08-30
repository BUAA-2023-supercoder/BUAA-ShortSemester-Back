import json
import random
from django.http import JsonResponse

from ProjectApi.models import Project, PrototypePage, Document
from TeamApi.models import Team, TeamMember
from UserApi.models import UserInfo
from summer_web.admin import getUserFromToken
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
            print(res)
            for item in res:
                team.append(item.teamID)
        else:
            team.append(Team.objects.get(id=teamID))
        print(team)
        Rye = list()
        projects = Project.objects.all().order_by('team_id')
        for item in projects:
            if item.team in team and item.isDelete is False:
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
        num = random.randint(1, 5)
        project = Project.objects.create(team=team,
                                         projectName=name if name is not None else 'untitled',
                                         image='ProjectProfile/' + str(num) + '.jpg',
                                         dict={
                                             'document': list(),
                                             'folder': list()
                                         })
        page = PrototypePage.objects.create(project=project,
                                            prototypeName='untitled',
                                            lastEditPerson=getUserFromToken(accessToken),
                                            context="",
                                            height=height,
                                            width=width)
        return JsonResponse({'msg': 'success', 'pageID': page.id, 'projectID': project.id}, status=200)
    else:
        return JsonResponse({'msg': 'fail', 'error': 'user does not exist'}, status=400)


def renameProject(request):
    if request.method != "PUT":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)

    accessToken = request.headers.get('Authorization').split(' ')[1]
    if validateAccessToken(accessToken):
        data = json.loads(request.body)
        projectID = data.get('projectID')
        name = data.get('name')
        project = Project.objects.get(id=projectID)
        if project is None:
            return JsonResponse({'msg': 'fail', 'error': 'project does not exist'}, status=400)
        if name is None:
            return JsonResponse({'msg': 'fail', 'error': 'new name can not be empty'}, status=400)
        project.projectName = name
        project.save()
        return JsonResponse({'msg': 'success'}, status=200)
    else:
        return JsonResponse({'msg': 'fail', 'error': 'login first please'}, status=400)


def changeProjectStatus(request):
    if request.method != "PUT":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)

    accessToken = request.headers.get('Authorization').split(' ')[1]
    if validateAccessToken(accessToken):
        data = json.loads(request.body)
        projectID = data.get('projectID')
        status = data.get('isDeleted')
        project = Project.objects.get(id=projectID)
        if project is None:
            return JsonResponse({'msg': 'fail', 'error': 'project does not exist'}, status=400)
        project.isDelete = status
        project.save()
        return JsonResponse({'msg': 'success'}, status=200)
    else:
        return JsonResponse({'msg': 'fail', 'error': 'login first please'}, status=400)

def getDeletedProject(request):
    if request.method != "POST":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)

    accessToken = request.headers.get('Authorization').split(' ')[1]
    if validateAccessToken(accessToken):
        data = json.loads(request.body)
        teamID = data.get('teamID')
        result = list()

        projects = Project.objects.all()

        for item in projects:
            if item.isDelete is True and item.team.id == teamID:
                info = {
                    'teamID': item.team.id,
                    'projectID': item.id,
                    'name': item.projectName,
                    'profile': URL + item.image.url
                }
                result.append(info)
        return JsonResponse({'msg': 'success', 'projects': result}, status=200)
    else:
        return JsonResponse({'msg': 'fail', 'error': 'login first please'}, status=400)

def getProjectInfo(request):
    if request.method != "POST":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)

    accessToken = request.headers.get('Authorization').split(' ')[1]
    if validateAccessToken(accessToken):
        projectID = json.loads(request.body).get('projectID')
        project = Project.objects.get(id=projectID)
        if project is None:
            return JsonResponse({'msg': 'fail', 'error': 'wrong projectID'}, status=400)
        docs = Document.objects.filter(project=project)
        page = PrototypePage.objects.get(project=project)
        if page is None:
            return JsonResponse({'msg': 'fail', 'error': 'PrototypePage missed, please check your database'}, status=400)
        docInfo = list()
        for item in docs:
            info = {
                'docID': item.id,
                'name': item.documentName,
                'lastEditTime': item.lastEditTime.strftime("%Y-%m-%d %H:%M:%S"),
                'lastEditPerson': item.lastEditPerson
            }
            docInfo.append(info)
        return JsonResponse({'msg': 'success',
                             'basicInfo': {
                                 'teamID': project.team.id,
                                 'projectName': project.projectName,
                                 'createTime': project.createTime.strftime("%Y-%m-%d %H:%M:%S"),
                                 'projectProfile': URL + project.image.url
                             },
                             'pagesInfo': {
                                 'pageID': page.id,
                                 'name': page.prototypeName,
                                 'lastEditTime': page.lastEditTime.strftime("%Y-%m-%d %H:%M:%S"),
                                 'lastEditPerson': page.lastEditPerson,
                                 'onEdit':  page.onEdit,
                                 'height': page.height,
                                 'width': page.width
                             },
                             'docInfo': docInfo}, status=200)
    else:
        return JsonResponse({'msg': 'fail', 'error': 'login first please'}, status=400)
