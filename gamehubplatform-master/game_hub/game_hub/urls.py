from django.contrib import admin
from django.urls import path, include
from django.conf import settings  # Thêm dòng này
from django.conf.urls.static import static  # Thêm dòng này
from player import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dash.urls')),
    path('player/', include('player.urls')),
    path('search-suggestions/', views.search_suggestions, name='search_suggestions'),

] 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
