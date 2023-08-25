from django.urls import path, include


from . import views

urlpatterns = [
    path('getprojects/', views.getProjectList),
    path('createproject/', views.createProject),
    path('deleteproject/', views.deleteProject),
    path('renameproject/', views.renameProject),
]