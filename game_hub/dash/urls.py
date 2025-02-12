from django.urls import path, include
from django.conf.urls.static import static
from . import views
from django.conf import settings

urlpatterns = [
    path('login/', views.login_view, name='login'), 
    path('register/', views.register, name='register'),  
    path('', views.index, name='index'),  
    path('player/', include('player.urls')),  

    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  