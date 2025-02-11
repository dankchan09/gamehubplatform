from django.urls import path, include
from django.conf.urls.static import static
from . import views
from django.conf import settings

urlpatterns = [
    path('login/', views.login_view, name='login'),  # Trang đăng nhập
    path('register/', views.register, name='register'),  # Trang đăng ký
    path('', views.index, name='index'),  # Trang chủ]
    path('player/', include('player.urls')),  # Điều hướng đến app player

    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # Đường dẫn tới thư mục media