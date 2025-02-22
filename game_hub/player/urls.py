from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
from .views import category_view
from .views import download_game

urlpatterns = [
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('logout/', views.user_logout, name='logout'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('product/<int:product_id>/submit_rating/', views.submit_rating, name='submit_rating'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('delete_review/<int:review_id>/', views.delete_review, name='delete_review'),
    path('edit_review/<int:review_id>/', views.edit_review, name='edit_review'),
    path('search-suggestions/', views.search_suggestions, name='search_suggestions'),
    path('add_funds/', views.add_funds, name='add_fund'),
    path('payment/', views.Payment, name='payment'),  
    path('library/', views.library, name='library'),
    path('product/<int:product_id>/purchase/', views.purchase_product, name='purchase_product'),
    path('guestdashboard/', views.index, name='guest_dashboard'),
    path('category/<str:category_key>/', category_view, name='category'),
    path('download/<int:product_id>/', download_game, name='download_game'),

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
