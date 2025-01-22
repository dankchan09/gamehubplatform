from django.db import models
from django.contrib.auth.models import User  # Kết nối với model User có sẵn của Django


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    full_name = models.CharField(max_length=255, blank=True, null=True)  # Họ và tên
    address = models.CharField(max_length=255, blank=True, null=True)     # Địa chỉ
    age = models.PositiveIntegerField(blank=True, null=True)              # Tuổi
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], blank=True, null=True)  # Giới tính

    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.jpg')  # Cập nhật đường dẫn mặc định cho avatar
    bio = models.TextField(null=True, blank=True)  # Mô tả cá nhân

    def __str__(self):
        return self.user.username


class UploadFile(models.Model):
    title = models.CharField(max_length=100)  # Tiêu đề file
    file = models.FileField(upload_to='uploads/')  # Thư mục 'uploads/' trong MEDIA_ROOT
    uploaded_at = models.DateTimeField(auto_now_add=True)  # Thời gian tải lên

    def __str__(self):
        return self.title


class Product(models.Model):
    CATEGORY_CHOICES = [
        ('adv', 'Adventure'),
        ('str', 'Strategy'),
        ('rac', 'Racing'),
        ('act', 'Action'),
        ('sim', 'Simulation'),
    ]

    name = models.CharField(max_length=200)  # Tên sản phẩm
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)  # Thể loại
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Giá gốc
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Giá giảm
    image = models.ImageField(upload_to='products/', default='products/default.jpg')  # Đường dẫn ảnh mặc định
    description = models.TextField(blank=True, null=True)  # Mô tả sản phẩm
    updated_at = models.DateTimeField(auto_now=True)  # Ngày cập nhật sản phẩm

    def __str__(self):
        return self.name

    def get_discount_percentage(self):
        if self.discount_price:
            return round((1 - self.discount_price / self.price) * 100, 2)
        return None


class ProductDetail(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='detail')  # Liên kết với sản phẩm
    additional_info = models.TextField(blank=True, null=True)  # Thông tin bổ sung
    specifications = models.TextField(blank=True, null=True)  # Thông số kỹ thuật
    tags = models.CharField(max_length=255, blank=True, null=True)  # Các thẻ liên quan (tags)

    def __str__(self):
        return f"Details of {self.product.name}"
