from django.urls import path,include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
urlpatterns = [
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('', views.player, name='player'),
    path('shop/', views.shop, name='shop'),
    path('upload file/', views.upload_file, name='upload_file'),
    path('upload success/', views.upload_success, name='upload_success'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)