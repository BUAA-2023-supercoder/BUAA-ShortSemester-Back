import json
import os

from django.db.models import Q
from django.http import JsonResponse
from django.utils.crypto import get_random_string

from summer_web.urls import URL
from .models import SingleMessage, SingleUnread
from UserApi.models import UserInfo, GENDER_ITEMS
from UserApi.admin import validateAccessToken, getUserFromToken


def addSingleMessage(request):
    if request.method != "POST":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)

    accessToken = request.headers.get('Authorization').split(' ')[1]
    if validateAccessToken(accessToken):
        data = request.POST
        receiver = UserInfo.objects.get(email=data.get('email'))
        sender = UserInfo.objects.get(email=getUserFromToken(accessToken))
        type = data.get('type')
        newMsg = SingleMessage.objects.create(sendUser=sender, receiveUser=receiver, type=0)
        if type == 'text':
            if data.get('text') is None:
                newMsg.delete()
                return JsonResponse({'msg': 'fail', 'error': 'text is None'}, status=400)

            newMsg.text = data.get('text')
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


def getSingleLateHistory(request):
    if request.method != "POST":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)

    accessToken = request.headers.get('Authorization').split(' ')[1]
    if validateAccessToken(accessToken):
        data = json.loads(request.body)
        email = data.get('email')
        cnt = data.get('times')
        if cnt is None:
            cnt = 50
        who = UserInfo.objects.get(email=email)
        if who is None:
            return JsonResponse({'msg': 'fail', 'error': 'can not find this user'}, status=400)
        user = UserInfo.objects.get(email=getUserFromToken(accessToken))
        records = list(SingleMessage.objects.filter(
            (Q(sendUser=user) & Q(receiveUser=who)) |
            (Q(sendUser=who) & Q(receiveUser=user))).order_by('time'))
        sz = len(records)
        result = list()
        for idx in range(max(0, sz - cnt), sz):
            item = records[idx]
            message = item.text
            if item.type == 1:
                message = URL + item.image.url
            elif item.type == 2:
                message = URL + item.file.url
            info = {
                'sendEmail': item.sendUser.email,
                'messageID': item.id,
                'time': item.time.strftime("%Y-%m-%d %H:%M:%S"),
                'type': item.type,
                'message': message
            }
            result.append(info)
        if SingleUnread.objects.filter(host=user, guest=who).count():
            SingleMessage.objects.get(host=user, guest=who).delete()
        return JsonResponse({'msg': 'success', 'chatHistory': result}, status=200)
    else:
        return JsonResponse({'msg': 'fail', 'error': 'please login first'}, statis=400)


def getHistory(request):
    if request.method != "POST":
        return JsonResponse({'msg': 'fail', 'error': 'wrong request method'}, status=500)

    accessToken = request.headers.get('Authorization').split(' ')[1]
    if validateAccessToken(accessToken):
        data = json.loads(request.body)
        email = data.get('email')
        ID = data.get('ID')
        singleMsg = SingleMessage.objects.get(id=ID)
        if singleMsg is None:
            return JsonResponse({'msg': 'fail', 'error': 'messageID is wrong'}, status=400)
        who = UserInfo.objects.get(email=email)
        if who is None:
            return JsonResponse({'msg': 'fail', 'error': 'the user email is wrong'}, status=400)
        endTime = singleMsg.time
        user = UserInfo.objects.get(email=getUserFromToken(accessToken))
        records = list(SingleMessage.objects.filter(
            ((Q(sendUser=user) & Q(receiveUser=who)) | (Q(sendUser=who) & Q(receiveUser=user)))
            & Q(time__lt=endTime)).order_by('time'))
        result = list()
        for idx in range(max(0, len(records) - 50), len(records)):
            item = records[idx]
            message = item.text
            if item.type == 1:
                message = URL + item.image.url
            elif item.type == 2:
                message = URL + item.file.url
            info = {
                'sendEmail': item.sendUser.email,
                'messageID': item.id,
                'time': item.time.strftime("%Y-%m-%d %H:%M:%S"),
                'type': item.type,
                'message': message
            }
            result.append(info)
        if SingleUnread.objects.filter(host=user, guest=who).count():
            SingleMessage.objects.get(host=user, guest=who).delete()
        return JsonResponse({'msg': 'success', 'chatHistory': result}, status=200)
    else:
        return JsonResponse({'msg': 'fail', 'error': 'please login first'}, statis=400)