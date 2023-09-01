import json
import os

from django.db.models import Q
from django.http import JsonResponse
from django.utils.crypto import get_random_string

from summer_web.urls import URL
from .models import SingleUnread, TeamMessage
from UserApi.models import UserInfo, GENDER_ITEMS
from UserApi.admin import validateAccessToken, getUserFromToken


def addSingleMessage(request):
    if request.method != "POST":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)

    accessToken = request.headers.get('Authorization').split(' ')[1]
    if validateAccessToken(accessToken):
        data = request.POST
        receiver = UserInfo.objects.get(email=data.get('receiver'))
        sender = UserInfo.objects.get(email=getUserFromToken(accessToken))
        type = data.get('type')
        newMsg = TeamMessage.objects.create(sendUser=sender, receiveUser=receiver, type=0, isGroup=False)
        if type == 'text':
            if data.get('text') is None:
                newMsg.delete()
                return JsonResponse({'msg': 'fail', 'error': 'text is None'}, status=400)

            newMsg.text = data.get('text')
            strAfter = data.get('text') + '@$%' + str(newMsg.id)

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
            newMsg.fileName = newMsg.file.split('/')[1]
            strAfter = '$$$' + 'Files' + '$$$' + newMsg.fileName + '@$%' + str(newMsg.id)
        else:
            newMsg.delete()
            return JsonResponse({'msg': 'fail', 'error': 'wrong message type'}, status=400)
        newMsg.save()

        # set unreadRecord
        '''
            host -> sender   guest -> receiver
            if A send B, then A(unread) == 0, B(unread) ++
        '''
        if SingleUnread.objects.filter(host=sender, guest=receiver).count() != 0:
            SingleUnread.objects.get(host=sender, guest=receiver).delete()  # A(unread) = 0
        if SingleUnread.objects.filter(host=receiver, guest=sender).count() == 0:
            SingleUnread.objects.create(host=receiver, guest=sender)
        else:
            obj = SingleUnread.objects.get(host=receiver, guest=sender)
            obj.cnt = obj.cnt + 1
            obj.save()                                                      # B(unread) ++

        return JsonResponse({'msg': 'success', 'str': strAfter, 'ID': newMsg.id}, status=200)
    else:
        return JsonResponse({'msg': 'fail', 'error': 'please login first'}, status=400)


def accessSingleChat(request):
    if request.method != "POST":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)

    accessToken = request.headers.get('Authorization').split(' ')[1]
    if validateAccessToken(accessToken):
        data = request.POST
        sender = UserInfo.objects.get(email=data.get('email'))
        receiver = UserInfo.objects.get(email=getUserFromToken(accessToken))
        if sender is None:
            return JsonResponse({'msg': 'fail', 'error': 'this email is wring'}, status=400)
        SingleUnread.objects.get(host=sender, guest=receiver).delete()
        return JsonResponse({'msg': 'success'}, status=200)
    else:
        return JsonResponse({'msg': 'fail', 'error': 'please login first'}, status=400)
