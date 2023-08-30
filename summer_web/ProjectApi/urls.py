from django.urls import path, include
from . import projects, docs, prototypePage

urlpatterns = [
    path('getprojects/', projects.getProjectList),
    path('createproject/', projects.createProject),
    path('deleteproject/', projects.changeProjectStatus),
    path('renameproject/', projects.renameProject),
    path('getdeletedproject/', projects.getDeletedProject),
    path('getprojectinfo/', projects.getProjectInfo),
    path('createfolder/', projects.createFolder),
    path('getdict/', projects.getDict),
    path('copyproject/', projects.copyProject),

    path('createdoc/', docs.createDoc),
    path('createsharelink/', docs.createShareLink),
    path('getdoc/', docs.getDoc),
    path('getsharedoc/<str:shareCode>', docs.getDocFromShare),
    path('savedoc/', docs.saveDoc),
    path('docat/', docs.docAt),
    path('getdocat/', docs.getDocAt),
    path('deldocat/', docs.delAtInfo),
    path('renamedoc/', docs.renameDoc),

    path('getpage/<int:pageID>', prototypePage.getPage),
    path('savepage/', prototypePage.savePage),
    path('renamepage/', prototypePage.renamePage)
]