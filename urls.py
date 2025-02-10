from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView

urlpatterns = [
    # URL cho trang hồ sơ và cập nhật thông tin
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    
    # Đường dẫn đăng xuất
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # Trang chủ hoặc trang người chơi
    path('', views.player, name='player'),
    
    # Chi tiết sản phẩm và chức năng đánh giá
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('product/<int:product_id>/submit_rating/', views.submit_rating, name='submit_rating'),
    
    # Các trang khác
    path('dashboard/', views.dashboard, name='dashboard'),
    path('delete_review/<int:review_id>/', views.delete_review, name='delete_review'),
    path('edit_review/<int:id>/', views.edit_review, name='edit_review'),
    path('search-suggestions/', views.search_suggestions, name='search_suggestions'),
    path('add_funds/', views.add_funds, name='add_fund'),

    # URL cho thanh toán (nếu chưa có)
    path('payment/', views.Payment, name='payment'),  # Thêm đường dẫn này nếu chưa có
    path('library/', views.library, name='library'),
    path('product/<int:product_id>/purchase/', views.purchase_product, name='purchase_product'),

]

# Cấu hình phục vụ media trong môi trường phát triển
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
