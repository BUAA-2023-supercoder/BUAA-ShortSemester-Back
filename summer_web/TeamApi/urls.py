from django.urls import path, include


from . import views

urlpatterns = [
    path('createteam/', views.createTeam),
    path('invitemember/', views.invite),
    path('setadmin/',views.setAdmin),
    path('removemember/',views.removeMember),
    path('setadmin/', views.setAdmin),
    path('allteam/', views.getAllTeam),
    path('allmember/', views.getAllMember),
    path('sendmessage/', views.addMessage),
    path('seteamprofile/', views.setTeamProfile)
]