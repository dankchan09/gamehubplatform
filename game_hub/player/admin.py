from django.contrib import admin
from .models import Product, ProductDetail, Review, Payment, Profile, Order, Library
from django.contrib import messages


# Quản lý sản phẩm
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'updated_at')  
    search_fields = ('name', 'category')
    list_filter = ('category', 'updated_at')

admin.site.register(Product, ProductAdmin)

# Quản lý chi tiết sản phẩm
class ProductDetailAdmin(admin.ModelAdmin):
    list_display = ('product', 'additional_info', 'tags')
    search_fields = ('product__name', 'tags')

admin.site.register(ProductDetail, ProductDetailAdmin)

# Quản lý đánh giá sản phẩm
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'comment', 'created_at', 'updated_at')
    search_fields = ('product__name', 'user__username', 'comment')
    list_filter = ('rating', 'created_at')

admin.site.register(Review, ReviewAdmin)

# Quản lý thanh toán
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'status', 'created_at']
    actions = ['approve_payment', 'refund_payment']

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

    def refund_payment(self, request, queryset):
        for payment in queryset:
            if payment.status == 'approved':
                payment.status = 'refunded'
                payment.save()

                # Giảm số dư cho người dùng (refund)
                profile = payment.user.profile
                profile.balance -= payment.amount
                profile.save()

                self.message_user(request, f"Số dư của {payment.user.username} đã được hoàn trả!")
            else:
                self.message_user(request, f"Thanh toán {payment.id} không thể hoàn trả hoặc đã bị hoàn trả.", level="error")

    refund_payment.short_description = "Hoàn trả thanh toán (xoá số dư)"

admin.site.register(Payment, PaymentAdmin)

class LibraryAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'added_at')
    search_fields = ('user__username', 'product__name')
    list_filter = ('added_at',)

admin.site.register(Library, LibraryAdmin)

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'username', 'age', 'gender', 'formatted_balance', 'library_count')
    search_fields = ('user__username', 'username')
    list_filter = ('gender', 'age')
    
    def formatted_balance(self, obj):
        return f"{obj.balance:,.0f} VND"
    formatted_balance.short_description = "Số dư (VND)"
    
    def library_count(self, obj):
        return obj.library.count()  
    library_count.short_description = "Số sản phẩm trong thư viện"

admin.site.register(Profile, ProfileAdmin)

class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    actions = ['approve_order', 'cancel_order', 'confirm_purchase_payment']  

    def approve_order(self, request, queryset):
        for order in queryset:
            if order.status == 'pending':
                order.status = 'approved'
                order.save()

                user_profile = order.user.profile
                user_profile.library.add(order.product)  

                self.message_user(request, f"Đơn hàng {order.id} đã được duyệt và thêm vào thư viện của {order.user.username}.")
            else:
                self.message_user(request, f"Đơn hàng {order.id} đã duyệt hoặc từ chối.", level="error")

    approve_order.short_description = "Duyệt đơn hàng"

    def cancel_order(self, request, queryset):
        for order in queryset:
            if order.status == 'approved':
                order.status = 'cancelled'
                order.save()
                self.message_user(request, f"Đơn hàng {order.id} đã bị hủy.")
            else:
                self.message_user(request, f"Đơn hàng {order.id} không thể hủy.", level="error")

    cancel_order.short_description = "Hủy đơn hàng"

    def confirm_purchase_payment(self, request, queryset):
        for order in queryset:
            if order.status == 'approved':
                self.message_user(request, f"Đơn hàng {order.id} đã được duyệt trước đó.", level="warning")
                continue

            if order.status == 'pending':
                user_profile = order.user.profile
                user_profile.balance -= order.total_price
                user_profile.save()
                order.status = 'approved'
                order.save()

                self.message_user(request, f"Thanh toán của người dùng {order.user.username} đã được duyệt.")

                messages.success(order.user, f"Bạn đã thanh toán thành công {order.total_price} VNĐ cho đơn hàng của mình.")
            else:
                self.message_user(request, f"Đơn hàng {order.id} không thể duyệt thanh toán.", level="error")

    confirm_purchase_payment.short_description = "Xác nhận thanh toán (trừ tiền tài khoản)"

admin.site.register(Order, OrderAdmin)

