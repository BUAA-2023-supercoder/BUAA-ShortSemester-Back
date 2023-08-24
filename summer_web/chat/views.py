from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
# 用于创建或进入聊天室
def newChat(request):
    return render(request, 'index.html', locals())

# 创建聊天室
def index(request):
    return render(request, "chat/index.html")
def room(request, room_name):
    return render(request, "chat/room.html", {"room_name": room_name})