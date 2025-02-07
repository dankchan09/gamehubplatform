from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.timezone import now
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.jpg')
    bio = models.TextField(null=True, blank=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Thêm trường số dư

    def __str__(self):
        return self.user.username

class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Chờ xử lý'),
        ('approved', 'Đã duyệt'),
        ('rejected', 'Từ chối'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100, unique=True, blank=True, null=True)
    created_at = models.DateTimeField(default=now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Payment {self.id} - {self.user.username} - {self.status}"

# Signal để cập nhật số dư khi thanh toán được duyệt
@receiver(post_save, sender=Payment)
def update_user_balance(sender, instance, **kwargs):
    if instance.status == 'approved':
        profile = instance.user.profile
        profile.balance += instance.amount
        profile.save()

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('adv', 'Adventure'),
        ('str', 'Strategy'),
        ('rac', 'Racing'),
        ('act', 'Action'),
        ('sim', 'Simulation'),
    ]

    name = models.CharField(max_length=200)
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, default='adv')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/', default='products/default.jpg')
    description = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def average_rating(self):
        # Lấy tất cả các đánh giá liên quan đến sản phẩm này
        reviews = self.reviews.all()
        if reviews.count() > 0:
            # Tính tổng điểm đánh giá
            total_rating = sum([review.rating for review in reviews])
            # Trả về điểm trung bình
            return total_rating / reviews.count()
        return 0  # Nếu không có đánh giá, trả về 0

class ProductDetail(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='detail')
    additional_info = models.TextField(blank=True, null=True)
    specifications = models.TextField(blank=True, null=True)
    tags = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Details of {self.product.name}"   


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i, f"{i} Star") for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)  # Thêm trường updated_at để theo dõi khi chỉnh sửa

    def __str__(self):
        return f"{self.user.username} - {self.product.name} Review"


class PlayerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Liên kết 1-1 với User
    other_field = models.CharField(max_length=100)  # Các trường khác cần thiết
    image = models.ImageField(upload_to='profile_pics', default='default.jpg')

    def __str__(self):
        return f"Profile of {self.user.username}"

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    order_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=50, default='pending')

    def __str__(self):
        return f"Order {self.id} - {self.product.name} by {self.user.username}"

