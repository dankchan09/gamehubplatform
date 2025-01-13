from django.urls import path
from . import views

urlpatterns = [
    path('members/',views.hello_world,name='home'),
    
]
