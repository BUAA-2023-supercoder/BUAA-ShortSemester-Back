from django.urls import path, include
from . import projects

urlpatterns = [
    path('getprojects/', projects.getProjectList),
    path('createproject/', projects.createProject),
    path('deleteproject/', projects.changeProjectStatus),
    path('renameproject/', projects.renameProject),
    path('getdeletedproject/', projects.getDeletedProject)
]