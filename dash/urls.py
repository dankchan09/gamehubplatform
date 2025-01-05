from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('guest/', views.guest, name='guest'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('login_process/', views.login_process, name='login_process'),

]
