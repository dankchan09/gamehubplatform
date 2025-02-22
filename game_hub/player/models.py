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

@receiver(post_save, sender=Payment)
def update_user_balance(sender, instance, **kwargs):
    if instance.status == 'approved':
        profile, created = Profile.objects.get_or_create(user=instance.user)
        profile.balance += instance.amount
        profile.save()


class Product(models.Model):
    CATEGORY_CHOICES = [
        ('adv', 'Phiêu lưu'),
        ('str', 'Kinh dị'),
        ('rac', 'Đua xe'),
        ('act', 'Hành động'),
        ('sim', 'Giả lập'),
    ]

    name = models.CharField(max_length=200)
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, default='adv')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/', default='products/default.jpg')
    description = models.TextField(blank=True, null=True)
    game_file = models.FileField(upload_to='game_files/', blank=True, null=True)
    stock = models.IntegerField(default=0)  
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
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name} Review"


class PlayerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    other_field = models.CharField(max_length=100)
    image = models.ImageField(upload_to='profile_pics', default='default.jpg')

    def __str__(self):
        return f"Profile of {self.user.username}"


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
        profile = self.user.profile
        if self.use_balance and profile.balance >= self.total_price:
            profile.balance -= self.total_price  # Trừ số dư tài khoản
            profile.save()
            self.status = 'approved'
        elif not self.use_balance or profile.balance < self.total_price:
            self.status = 'approved'
        else:
            self.status = 'rejected'
        
        if self.status == 'approved':
            Library.objects.get_or_create(user=self.user, product=self.product)

        self.save()

class Library(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(default=timezone.now)  


    class Meta:
        unique_together = ('user', 'product')  

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


