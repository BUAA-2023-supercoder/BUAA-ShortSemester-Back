import datetime
import json
import random
from django.http import JsonResponse

from ProjectApi.models import Project, PrototypePage, Document
from TeamApi.models import Team, TeamMember
from UserApi.models import UserInfo
from summer_web.admin import getUserFromToken
from UserApi.admin import validateAccessToken, getUserFromToken
from summer_web.urls import URL


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
        return JsonResponse({'msg': 'success', 'docID': doc.id}, status=200)
    else:
        return JsonResponse({'msg': 'fail', 'error': 'user does not exist'}, status=400)

def saveDoc(request):
    if request.method != "POST":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)

    data = json.loads(request.body)
    context = data.get('context')
    person = data.get('email')
    docID = data.get('docID')
    doc = Document.objects.get(id=docID)
    if doc is None:
        return JsonResponse({'msg': 'fail', 'error': 'docID is missed'}, status=400)
    if context is None:
        return JsonResponse({'msg': 'fail', 'error': 'context can not be null'}, status=400)
    doc.context = context
    doc.lastEditPerson = '游客' if person is None else person
    doc.lastEditTime = datetime.datetime.now()
    doc.save()
    return JsonResponse({'msg': 'success'}, status=200)
