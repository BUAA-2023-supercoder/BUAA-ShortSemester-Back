from django.urls import path, include


import views
urlpatterns = [
    # path('admin/', admin.site.urls),

    path('api/createteam/', views.createTeam),
    path('api/invitemember/',views.invite)
]