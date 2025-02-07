from django.urls import path,include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
from django.urls import path, include

urlpatterns = [
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('', views.player, name='player'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('product/<int:product_id>/submit_rating/', views.submit_rating, name='submit_rating'),
    path('delete_review/<int:review_id>/', views.delete_review, name='delete_review'),
    path('edit_review/<int:id>/', views.edit_review, name='edit_review'),
    path('search-suggestions/', views.search_suggestions, name='search_suggestions'),
    path('payment/', views.payment, name='payment'),
    
   
    

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)