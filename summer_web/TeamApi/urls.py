from django.urls import path, include


from . import views

urlpatterns = [
    path('createteam/', views.createTeam),
    path('invitemember/', views.invite),
    path('setadmin/',views.setAdmin),
    path('removemember/',views.remove_member)
]