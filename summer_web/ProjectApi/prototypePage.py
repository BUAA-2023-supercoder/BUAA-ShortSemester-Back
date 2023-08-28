import datetime
import json
from django.http import JsonResponse
from django.utils.crypto import get_random_string

from ProjectApi.models import Project, PrototypePage, Document, ShareLink, DocAt
from TeamApi.models import TeamMember
from UserApi.models import UserInfo
from summer_web.admin import getUserFromToken
from UserApi.admin import validateAccessToken, getUserFromToken

def getPage(request, pageID):
    if request.method != "GET":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)

    accessToken = request.headers.get('Authorization').split(' ')[1]
    if validateAccessToken(accessToken):
        page = PrototypePage.objects.get(id=pageID)
        user = UserInfo.objects.get(email=getUserFromToken(accessToken))
        if page is None:
            return JsonResponse({'msg': 'fail', 'error': 'pageID is wrong'}, status=400)
        if TeamMember.objects.filter(member=user, teamID=page.project.team).count() == 0:
            return JsonResponse({'msg': 'fail', 'error': 'you should not access this page'}, status=400)
        info = {
            'onEdit': page.onEdit,
            'context': page.context,
            'ID': page.id,
            'height': page.height,
            'width': page.width,
            'name': page.prototypeName,
            'lastEditTime': page.lastEditTime.strftime("%Y-%m-%d %H:%M:%S"),
            'lastEditPerson': page.lastEditPerson,
            'projectID': page.project.id
        }
        return JsonResponse({'msg': 'success', 'info': info}, status=200)
    else:
        return JsonResponse({'msg': 'fail', 'error': 'user does not exist'}, status=400)


def savePage(request):
    if request.method != "POST":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)

    accessToken = request.headers.get('Authorization').split(' ')[1]
    if validateAccessToken(accessToken):
        data = json.loads(request.body)
        pageID = data.get('pageID')
        context = data.get('context')
        onEdit = data.get('onEdit')
        page = PrototypePage.objects.get(id=pageID)
        if page is None:
            return JsonResponse({'msg': 'fail', 'error': 'pageID is wrong'}, status=400)
        user = UserInfo.objects.get(email=getUserFromToken(accessToken))
        if TeamMember.objects.filter(member=user, teamID=page.project.team).count() == 0:
            return JsonResponse({'msg': 'fail', 'error': 'Theoretically, you should not see this'}, status=400)
        page.context = context
        page.onEdit = onEdit
        page.lastEditTime = datetime.datetime.now()
        page.lastEditPerson = user.email
        page.save()
        return JsonResponse({'msg': 'success'}, status=200)
    else:
        return JsonResponse({'msg': 'fail', 'error': 'user does not exist'}, status=400)


def renamePage(request):
    if request.method != "POST":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)

    accessToken = request.headers.get('Authorization').split(' ')[1]
    if validateAccessToken(accessToken):
        pageID = json.loads(request.body).get('pageID')
        name = json.loads(request.body).get('name')
        page = PrototypePage.objects.get(id=pageID)
        if page is None:
            return JsonResponse({'msg': 'fail', 'error': 'pageID is wrong'}, status=400)
        user = UserInfo.objects.get(email=getUserFromToken(accessToken))
        if TeamMember.objects.filter(member=user, teamID=page.project.team).count() == 0:
            return JsonResponse({'msg': 'fail', 'error': 'Theoretically, you should not see this'}, status=400)
        page.prototypeName = name
        page.save()
        return JsonResponse({'msg': 'success'}, status=200)
    else:
        return JsonResponse({'msg': 'fail', 'error': 'user does not exist'}, status=400)
