from django.urls import path, include


from . import views, single, chatGroup

urlpatterns = [
    path('createteam/', views.createTeam),
    path('invitemember/', views.invite),
    path('setadmin/',views.setAdmin),
    path('removemember/',views.removeMember),
    path('setadmin/', views.setAdmin),
    path('allteam/', views.getAllTeam),
    path('allmember/', views.getAllMember),
    path('allfriends/', views.getAllFriends),
    path('sendmessage/', views.addMessage),
    path('seteamprofile/', views.setTeamProfile),
    path('messageat/', views.messageAt),
    path('getatmessage/', views.getAtMessage),
    path('skiptoatinteam/', views.skipToAtPosition),
    path('readatmessage/', views.readAtMessage),
    path('accessteamgroup/', views.accessTeamChat),
    path('getunread/', views.getUnreadInfo),


    path('chathistory/', views.getHistory),
    path('deleteatmsg/', views.deleteAtMsg),
    path('getlatemessage/', views.getLateHistory),

    path('sendsinglemsg/', single.addSingleMessage),
    path('accessingle/', single.accessSingleChat),

    path('createchatgroup/', chatGroup.createChatGroup),
    path('addtochatgroup/', chatGroup.addToChatGroup),
    path('runrunrun/', chatGroup.delFromChatGroup),
    path('delchatgroup/', chatGroup.delTotalChatGroup)
]