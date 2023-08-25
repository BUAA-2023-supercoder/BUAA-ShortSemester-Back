from django.urls import path, include


from . import views

urlpatterns = [
    path('login/', views.login),
    path('sendemail/', views.sendEmail),
    path('register/', views.register),
    path('setprofile/', views.setProfile),
    path('getinfo/', views.getInfo),
    path('changeinfo/', views.changeInfo)
]