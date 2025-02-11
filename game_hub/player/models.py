from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.timezone import now
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid
from django.utils.formats import number_format

# Mô hình Profile cho người dùng
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    username = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', default='IMG/man_default.png')
    bio = models.TextField(null=True, blank=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    library = models.ManyToManyField('Library', related_name='profiles', blank=True)


    def __str__(self):
        return self.user.username


# Mô hình Payment (Thanh toán)
class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Chờ xử lý'),
        ('approved', 'Đã duyệt'),
        ('rejected', 'Từ chối'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(default=now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    order = models.ForeignKey('Order', on_delete=models.CASCADE, null=True, blank=True)  # Liên kết với Order

    def __str__(self):
        return f"Payment {self.id} - {self.user.username} - {self.status}"


# Tự động cập nhật số dư người dùng khi thanh toán được duyệt
@receiver(post_save, sender=Payment)
def update_user_balance(sender, instance, **kwargs):
    if instance.status == 'approved':
        profile, created = Profile.objects.get_or_create(user=instance.user)
        profile.balance += instance.amount
        profile.save()


# Mô hình Product (Sản phẩm)
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
    stock = models.IntegerField(default=0)  # Số lượng sản phẩm
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    def formatted_price(self):
        return f"{number_format(self.price, 0)} VND"

    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews.count() > 0:
            total_rating = sum([review.rating for review in reviews])
            return total_rating / reviews.count()
        return 0


# Mô hình ProductDetail (Chi tiết sản phẩm)
class ProductDetail(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='detail')
    additional_info = models.TextField(blank=True, null=True)
    specifications = models.TextField(blank=True, null=True)
    tags = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Details of {self.product.name}"


# Mô hình Review (Đánh giá sản phẩm)
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i, f"{i} Star") for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name} Review"


# Mô hình PlayerProfile (Hồ sơ người chơi)
class PlayerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    other_field = models.CharField(max_length=100)
    image = models.ImageField(upload_to='profile_pics', default='default.jpg')

    def __str__(self):
        return f"Profile of {self.user.username}"


# Mô hình Order (Đơn hàng)
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    order_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=50, default='pending')
    use_balance = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)  # Chỉ giữ default=timezone.now

    def __str__(self):
        return f"Order {self.id} - {self.product.name} by {self.user.username}"

    def process_order(self):
        """
        Xử lý đơn hàng, tính toán và trừ số dư tài khoản nếu có sử dụng số dư.
        Sau khi đơn hàng được xử lý thành công, thêm sản phẩm vào thư viện người dùng.
        """
        profile = self.user.profile
        if self.use_balance and profile.balance >= self.total_price:
            profile.balance -= self.total_price  # Trừ số dư tài khoản
            profile.save()
            self.status = 'approved'
        elif not self.use_balance or profile.balance < self.total_price:
            self.status = 'approved'
        else:
            self.status = 'rejected'
        
        # Nếu đơn hàng được duyệt, thêm sản phẩm vào thư viện
        if self.status == 'approved':
            Library.objects.get_or_create(user=self.user, product=self.product)

        self.save()

class Library(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(default=timezone.now)  # Dùng default thay vì auto_now_add


    class Meta:
        unique_together = ('user', 'product')  # Một sản phẩm chỉ có thể xuất hiện 1 lần trong thư viện của mỗi người dùng

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


