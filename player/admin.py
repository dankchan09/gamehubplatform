from django.contrib import admin
from .models import Product, ProductDetail
from .models import Review
from .models import Payment

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'updated_at')  
    search_fields = ('name', 'category')
    list_filter = ('category', 'updated_at')

admin.site.register(Product, ProductAdmin)

class ProductDetailAdmin(admin.ModelAdmin):
    list_display = ('product', 'additional_info', 'tags')
    search_fields = ('product__name', 'tags')

admin.site.register(ProductDetail, ProductDetailAdmin)

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'comment', 'created_at', 'updated_at')
    search_fields = ('product__name', 'user__username', 'comment')
    list_filter = ('rating', 'created_at')

admin.site.register(Review, ReviewAdmin)

class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'status', 'created_at']
    actions = ['approve_payment']

    def approve_payment(self, request, queryset):
        for payment in queryset:
            if payment.status == 'pending':
                payment.status = 'approved'
                payment.save()

                # Cập nhật số dư cho người dùng
                profile = payment.user.profile
                profile.balance += payment.amount
                profile.save()

                self.message_user(request, f"Thanh toán của {payment.user.username} đã được duyệt!")
            else:
                self.message_user(request, f"Thanh toán {payment.id} đã được duyệt hoặc từ chối.", level="error")

    approve_payment.short_description = "Duyệt thanh toán"

admin.site.register(Payment, PaymentAdmin)