from django.urls import path, include
from . import projects, docs

urlpatterns = [
    path('getprojects/', projects.getProjectList),
    path('createproject/', projects.createProject),
    path('deleteproject/', projects.changeProjectStatus),
    path('renameproject/', projects.renameProject),
    path('getdeletedproject/', projects.getDeletedProject),
    path('getprojectinfo/', projects.getProjectInfo),

    path('createdoc/', docs.createDoc),
    path('createsharelink/', docs.createShareLink),
    path('getdoc/', docs.getDoc),
    path('getsharedoc/<str:shareCode>', docs.getDocFromShare),
    path('savedoc/', docs.saveDoc)
]