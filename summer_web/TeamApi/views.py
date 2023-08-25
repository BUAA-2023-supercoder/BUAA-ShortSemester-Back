import json

from django.http import JsonResponse
from django.shortcuts import render
from TeamApi.models import Team, TeamMember
from UserApi.models import UserInfo


# Create your views here.
def createTeam(request):
    if request.method != "POST":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)

    data = json.loads(request.body)
    member = UserInfo.objects.get(email=data.get('email'))
    name = data.get('name')
    try:
        team = Team.objects.create(creator=member, name=name)
        TeamMember.objects.create(member=member, teamID=team, role=0)
        return JsonResponse({'msg': 'success'}, status=200)
    except Exception as e:
        return JsonResponse({'msg': 'fail', 'error': str(e)}, status=500)
