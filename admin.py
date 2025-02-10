from django.contrib import admin
from .models import Product, ProductDetail, Review, Payment, Profile, Order
from django.contrib import messages
from django.utils.formats import number_format


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

# Quản lý hồ sơ người dùng
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'age', 'gender', 'formatted_balance', 'avatar')
    search_fields = ('user__username', 'full_name')
    list_filter = ('gender', 'age')

    def formatted_balance(self, obj):
        # Định dạng số dư thành VND với dấu phẩy cho dễ đọc
        return f"{obj.balance:,.0f} VND"
    formatted_balance.short_description = "Số dư (VND)"

admin.site.register(Profile, ProfileAdmin)

# Quản lý đơn hàng
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    actions = ['approve_order', 'cancel_order', 'confirm_purchase_payment']  # Thêm hành động confirm_payment

    def approve_order(self, request, queryset):
        for order in queryset:
            if order.status == 'pending':
                order.status = 'approved'
                order.save()

                # Cập nhật thư viện người dùng với sản phẩm đã mua
                user_profile = order.user.profile
                user_profile.library.add(order.product)  # Giả sử bạn đã thêm thư viện vào Profile model

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
                # Trừ số tiền từ tài khoản người dùng
                user_profile = order.user.profile
                user_profile.balance -= order.total_price
                user_profile.save()

                # Cập nhật trạng thái đơn hàng thành 'approved'
                order.status = 'approved'
                order.save()

                # Thông báo người dùng về giao dịch thành công
                self.message_user(request, f"Thanh toán của người dùng {order.user.username} đã được duyệt.")

                # Gửi thông báo cho người dùng
                messages.success(order.user, f"Bạn đã thanh toán thành công {order.total_price} VNĐ cho đơn hàng của mình.")
            else:
                self.message_user(request, f"Đơn hàng {order.id} không thể duyệt thanh toán.", level="error")

    confirm_purchase_payment.short_description = "Xác nhận thanh toán (trừ tiền tài khoản)"

admin.site.register(Order, OrderAdmin)

