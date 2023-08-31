import datetime
import json
import random
import time

from django.http import JsonResponse
from pyasn1.compat.octets import null

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
        order = json.loads(request.body).get('order')
        team = list()
        if teamID is None:
            res = TeamMember.objects.filter(member=user)
            print(res)
            for item in res:
                team.append(item.teamID)
        else:
            team.append(Team.objects.get(id=teamID))
        Rye = list()
        if order is None or order == 'default':
            projects = Project.objects.all().order_by('team_id')
        elif order == 'time':
            projects = Project.objects.all().order_by('-createTime')
        elif order == 'name':
            projects = Project.objects.all().order_by('projectName')
        else:
            return JsonResponse({'msg': 'fail', 'error': 'wrong method about order'}, status=400)
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
                                             'folder': dict()
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

def copyProject(request):
    if request.method != "POST":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)

    accessToken = request.headers.get('Authorization').split(' ')[1]
    if validateAccessToken(accessToken):
        projectID = json.loads(request.body).get('projectID')
        project = Project.objects.get(id=projectID)
        if project is None:
            return JsonResponse({'msg': 'fail', 'error': 'wrong projectID'}, status=400)
        num = random.randint(1, 5)
        newProject = Project.objects.create(team=project.team,
                                            projectName=project.projectName + ' - 副本',
                                            image='ProjectProfile/' + str(num) + '.jpg',
                                            dict=project.dict)
        oldPage = PrototypePage.objects.get(id=project.id)
        page = PrototypePage.objects.create(project=newProject,
                                            prototypeName=oldPage.prototypeName,
                                            lastEditPerson=getUserFromToken(accessToken),
                                            context=oldPage.context,
                                            height=oldPage.height,
                                            width=oldPage.width)
        dit = {
            "folder": dict(),
            "document": list()
        }
        for item in project.dict['document']:
            doc = Document.objects.get(id=item)
            newDoc = Document.objects.create(project=newProject,
                                             documentName=doc.documentName,
                                             context=doc.context,
                                             lastEditPerson=getUserFromToken(accessToken))
            dit['document'].append(newDoc.id)
        for key, val in project.dict['folder'].items():
            info = list()
            for item in val['documents']:
                doc = Document.objects.get(id=item)
                newDoc = Document.objects.create(project=newProject,
                                                 documentName=doc.documentName,
                                                 context=doc.context,
                                                 lastEditPerson=getUserFromToken(accessToken))
                info.append(newDoc.id)
            dit['folder'][key] = {
                'createTime': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'createPerson': UserInfo.objects.get(email=getUserFromToken(accessToken)).email,
                'documents': info
            }
        newProject.dict = dit
        newProject.save()
        return JsonResponse({'msg': 'success', 'pageID': page.id, 'projectID': newProject.id}, status=200)
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


def createFolder(request):
    if request.method != "POST":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)

    accessToken = request.headers.get('Authorization').split(' ')[1]
    if validateAccessToken(accessToken):
        projectID = json.loads(request.body).get('projectID')
        name = json.loads(request.body).get('name')
        project = Project.objects.get(id=projectID)
        if project is None:
            return JsonResponse({'msg': 'fail', 'error': 'wrong projectID'}, status=400)
        if name in project.dict['folder']:
            return JsonResponse({'msg': 'fail', 'error': 'the folder name can not be same!!'}, status=201)
        folderInfo = {
            'createTime': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'createPerson': UserInfo.objects.get(email=getUserFromToken(accessToken)).email,
            'documents': list()
        }
        project.dict['folder'][name] = folderInfo
        project.save()
        return JsonResponse({'msg': 'success'}, status=200)
    else:
        return JsonResponse({'msg': 'fail', 'error': 'login first please'}, status=400)



def folderRename(request):
    if request.method != "POST":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)

    accessToken = request.headers.get('Authorization').split(' ')[1]
    if validateAccessToken(accessToken):
        data = json.loads(request.body)
        oldName = data.get('oldName')
        newName = data.get('newName')
        projectID = data.get('projectID')
        project = Project.objects.get(id=projectID)
        if project is None:
            return JsonResponse({'msg': 'fail', 'error': 'projectID is wrong'}, status=400)
        info = project.dict['folder'][oldName]
        del project.dict['folder'][oldName]
        project.dict['folder'][newName] = info
        project.save()
        return JsonResponse({'msg': 'success'}, status=200)
    else:
        return JsonResponse({'msg': 'fail', 'error': 'login first please'}, status=400)


def checkTime(time1, time2):
    t1 = time.strptime(time1, '%Y-%m-%d %H:%M:%S')
    t2 = time.strptime(time2, '%Y-%m-%d %H:%M:%S')
    return t1 < t2


def getDict(request):
    if request.method != "POST":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)

    accessToken = request.headers.get('Authorization').split(' ')[1]
    if validateAccessToken(accessToken):
        projectID = json.loads(request.body).get('projectID')
        project = Project.objects.get(id=projectID)
        if project is None:
            return JsonResponse({'msg': 'fail', 'error': 'wrong projectID'}, status=400)

        documents = list()
        for ID in project.dict['document']:
            obj = Document.objects.get(id=ID)
            docInfo = {
                'ID': obj.id,
                'name': obj.documentName,
                'lastEditTime': obj.lastEditTime.strftime("%Y-%m-%d %H:%M:%S"),
                'lastEditPerson': obj.lastEditPerson
            }
            documents.append(docInfo)
        folders = list()
        for key, val in project.dict['folder'].items():
            info = {
                'name': key,
                'createTime': val['createTime'],
                'createPerson': val['createPerson'],
                'lastEditTime': val['createTime'],
                'lastEditPerson': val['createPerson'],
                'documents': list()
            }
            for ID in val['documents']:
                obj = Document.objects.get(id=ID)
                docInfo = {
                    'ID': obj.id,
                    'name': obj.documentName,
                    'lastEditTime': obj.lastEditTime.strftime("%Y-%m-%d %H:%M:%S"),
                    'lastEditPerson': obj.lastEditPerson
                }
                info['documents'].append(docInfo)
                if checkTime(info['lastEditTime'], docInfo['lastEditTime']):
                    info['lastEditTime'] = docInfo['lastEditTime']
                    info['lastEditPerson'] = docInfo['lastEditPerson']
            folders.append(info)
        return JsonResponse({'msg': 'success', 'dict': {'documents': documents, 'folders': folders}}, status=200)
    else:
        return JsonResponse({'msg': 'fail', 'error': 'login first please'}, status=400)
