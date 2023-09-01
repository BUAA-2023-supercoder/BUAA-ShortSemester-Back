import datetime
import json
from django.http import JsonResponse
from django.utils.crypto import get_random_string

from ProjectApi.models import Project, PrototypePage, Document, ShareLink, DocAt, DocVersion
from TeamApi.models import TeamMember
from UserApi.models import UserInfo
from summer_web.admin import getUserFromToken
from UserApi.admin import validateAccessToken, getUserFromToken


def createDoc(request):
    if request.method != "POST":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)

    accessToken = request.headers.get('Authorization').split(' ')[1]
    if validateAccessToken(accessToken):
        data = json.loads(request.body)
        projectID = data.get('projectID')
        project = Project.objects.get(id=projectID)
        if project is None:
            return JsonResponse({'msg': 'fail', 'error': 'projectID is wrong'}, status=400)
        name = data.get('name')
        doc = Document.objects.create(project=project,
                                      documentName=name,
                                      context="",
                                      lastEditPerson=getUserFromToken(accessToken))
        folderName = data.get('folder')
        if folderName is None:
            print(project.dict['document'])
            project.dict['document'].append(doc.id)
        else:
            if folderName not in project.dict['folder']:
                return JsonResponse({'msg': 'fail', 'error': 'wrong folder name'}, status=204)
            else:
                project.dict['folder'][folderName]['documents'].append(doc.id)
        project.save()
        return JsonResponse({'msg': 'success', 'docID': doc.id}, status=200)
    else:
        return JsonResponse({'msg': 'fail', 'error': 'user does not exist'}, status=400)

def saveDoc(request):
    if request.method != "POST":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)

    data = json.loads(request.body)
    context = data.get('context')
    docID = data.get('docID')
    save = data.get('saveVersion')
    doc = Document.objects.get(id=docID)
    shareCode = data.get('shareCode')
    if doc is None:
        return JsonResponse({'msg': 'fail', 'error': 'docID is missed'}, status=400)
    if context is None:
        return JsonResponse({'msg': 'fail', 'error': 'context can not be null'}, status=400)
    if shareCode is None or request.headers.get('Authorization') is None:
        accessToken = request.headers.get('Authorization').split(' ')[1]
        if validateAccessToken(accessToken):
            user = UserInfo.objects.get(email=getUserFromToken(accessToken))
            doc.lastEditPerson = user.email
            doc.lastEditTime = datetime.datetime.now()
        else:
            JsonResponse({'msg': 'fail', 'error': 'user does not exist'}, status=400)
    else:
        link = ShareLink.objects.get(str=shareCode)
        if link is None:
            return JsonResponse({'msg': 'fail', 'error': 'this shareLink does not exist'}, status=400)
        if link.isWrite is not True:
            return JsonResponse({'msg': 'fail', 'error': 'this shareLink can only read'}, status=400)
        if link.validity < datetime.datetime.now():
            return JsonResponse({'msg': 'fail', 'error': 'this shareLink is expired'}, status=400)
        doc.lastEditPerson = 'null@163.com'     # 游客
        doc.lastEditTime = datetime.datetime.now()
    doc.context = context
    doc.save()
    if save is not None and save:
        cnt = DocVersion.objects.filter(docID=doc.id).count()
        DocVersion.objects.create(docID=doc.id, context=context, version=cnt+1)
    return JsonResponse({'msg': 'success'}, status=200)


def getVersion(request):
    if request.method != "POST":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)

    docID = json.loads(request.body).get('docID')
    res = DocVersion.objects.filter(docID=docID).order_by('saveTime')
    result = list()
    for item in res:
        info = {
            'version': item.version,
            'saveTime': item.saveTime.strftime("%Y-%m-%d %H:%M:%S"),
            'context': item.context
        }
        result.append(info)
    return JsonResponse({'msg': 'success', 'version': result}, status=200)


def createShareLink(request):
    if request.method != "POST":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)

    accessToken = request.headers.get('Authorization').split(' ')[1]
    if validateAccessToken(accessToken):
        data = json.loads(request.body)
        docID = data.get('docID')
        doc = Document.objects.get(id=docID)
        if doc is None:
            return JsonResponse({'msg': 'fail', 'error': 'docID is missed'}, status=400)
        time = data.get('validity')
        validity = datetime.datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
        if datetime.datetime.now() > validity:
            return JsonResponse({'msg': 'fail', 'error': 'the validity can not earlier than now'}, status=400)
        isWrite = data.get('isWrite')
        shareCode = get_random_string(length=10)
        ShareLink.objects.create(str=shareCode, document=doc, validity=validity, isWrite=isWrite)
        return JsonResponse({'msg': 'success', 'shareCode': shareCode}, status=200)
    else:
        return JsonResponse({'msg': 'fail', 'error': 'user does not exist'}, status=400)


def getDoc(request):
    if request.method != "POST":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)

    accessToken = request.headers.get('Authorization').split(' ')[1]
    if validateAccessToken(accessToken):
        docID = json.loads(request.body).get('docID')
        doc = Document.objects.get(id=docID)
        if doc is None:
            return JsonResponse({'msg': 'fail', 'error': 'docID is wrong'}, status=400)
        user = UserInfo.objects.get(email=getUserFromToken(accessToken))
        if TeamMember.objects.filter(member=user, teamID=doc.project.team).count() == 0:
            return JsonResponse({'msg': 'fail', 'error': 'you can no permission'}, status=400)
        return JsonResponse({'msg': 'success',
                             'teamID': doc.project.team.id,
                             'doc': {
                                 'docID': doc.id,
                                 'context': doc.context,
                                 'name': doc.documentName,
                                 'lastEditTime': doc.lastEditTime.strftime("%Y-%m-%d %H:%M:%S"),
                                 'lastEditPerson': doc.lastEditPerson}
                             }, status=200)
    else:
        return JsonResponse({'msg': 'fail', 'error': 'user does not exist'}, status=400)

def getDocFromShare(request, shareCode):
    if request.method != 'GET':
        return JsonResponse({'message': 'fail', 'error': 'wrong request method'}, status=400)

    link = ShareLink.objects.get(str=shareCode)
    if link is None:
        return JsonResponse({'msg': 'fail', 'error': 'shareCode does not exist'}, status=400)
    if link.validity < datetime.datetime.now():
        return JsonResponse({'msg': 'fail', 'error': 'this shareCode has expired'}, status=400)
    return JsonResponse({'msg': 'success',
                         'isWrite': link.isWrite,
                         'validity': link.validity.strftime("%Y-%m-%d %H:%M:%S"),
                         'doc': {
                             'docID': link.document.id,
                             'context': link.document.context,
                             'name': link.document.documentName
                         }}, status=200)


# def atDoc()

def docAt(request):
    if request.method != "POST":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)

    accessToken = request.headers.get('Authorization').split(' ')[1]
    if validateAccessToken(accessToken):
        email = json.loads(request.body).get('email')
        docID = json.loads(request.body).get('docID')
        user = UserInfo.objects.get(email=email)
        doc = Document.objects.get(id=docID)
        if doc is None:
            return JsonResponse({'msg': 'fail', 'error': 'docID is wrong'}, status=400)
        if TeamMember.objects.filter(teamID=doc.project.team, member=user).count() == 0:
            return JsonResponse({'msg': 'fail', 'error': 'this man is not in the team'}, status=400)
        if DocAt.objects.filter(member=user, document=doc).count() == 0:
            DocAt.objects.create(member=user, document=doc)
        return JsonResponse({'msg': 'success'}, status=200)
    else:
        return JsonResponse({'msg': 'fail', 'error': 'user does not exist'}, status=400)

def renameDoc(request):
    if request.method != "POST":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)

    accessToken = request.headers.get('Authorization').split(' ')[1]
    if validateAccessToken(accessToken):
        docID = json.loads(request.body).get('docID')
        name = json.loads(request.body).get('name')
        doc = Document.objects.get(id=docID)
        user = UserInfo.objects.get(email=getUserFromToken(accessToken))
        if doc is None:
            return JsonResponse({'msg': 'fail', 'error': 'docID is wrong'}, status=400)
        if TeamMember.objects.filter(teamID=doc.project.team, member=user).count() == 0:
            return JsonResponse({'msg': 'fail', 'error': 'you have no permission to rename'}, status=400)
        doc.documentName = name
        doc.save()
        return JsonResponse({'msg': 'success'}, status=200)
    else:
        return JsonResponse({'msg': 'fail', 'error': 'user does not exist'}, status=400)

def getDocAt(request):
    if request.method != "POST":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)

    accessToken = request.headers.get('Authorization').split(' ')[1]
    if validateAccessToken(accessToken):
        user = UserInfo.objects.get(email=getUserFromToken(accessToken))
        if user is None:
            return JsonResponse({'msg': 'fail', 'error': 'user does not exist'}, status=400)
        records = DocAt.objects.filter(member=user).order_by('document_id')
        result = list()
        for item in records:
            info = {
                'docID': item.document.id,
                'name': item.document.documentName,
                'projectID': item.document.project.id,
                'projectName': item.document.project.projectName,
                'teamID': item.document.project.team.id
            }
            result.append(info)
        return JsonResponse({'msg': 'success', 'result': result}, status=200)
    else:
        return JsonResponse({'msg': 'fail', 'error': 'user does not exist'}, status=400)

def delAtInfo(request):
    if request.method != "POST":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)

    accessToken = request.headers.get('Authorization').split(' ')[1]
    if validateAccessToken(accessToken):
        user = UserInfo.objects.get(email=getUserFromToken(accessToken))
        if user is None:
            return JsonResponse({'msg': 'fail', 'error': 'user does not exist'}, status=400)
        docID = json.loads(request.body).get('docID')
        doc = Document.objects.get(id=docID)
        if doc is None:
            return JsonResponse({'msg': 'fail', 'error': 'docID is wrong'}, status=400)
        DocAt.objects.get(document=doc, member=user).delete()
        return JsonResponse({'msg': 'success'}, status=200)
    else:
        return JsonResponse({'msg': 'fail', 'error': 'user does not exist'}, status=400)

