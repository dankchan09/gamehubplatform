from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Avg, F
from django.http import JsonResponse, Http404
from .models import Profile, Product, Review, Payment, Order, Library
from .forms import ProfileUpdateForm, ReviewForm
import json
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.urls import reverse
from django.db import transaction

def format_vnd(value):
    return f"{value:,} VNĐ"

# Trang chủ của người chơi
def player(request):
    return render(request, 'base.html')

# Trang thông tin cá nhân người chơi
@login_required
def profile(request):
    return render(request, 'profile.html', {'profile': request.user.profile})

# Cập nhật thông tin cá nhân
@login_required
def update_profile(request):
    if not hasattr(request.user, 'profile'):
        Profile.objects.create(user=request.user)

    profile = request.user.profile

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cập nhật thông tin thành công!')
            return redirect(reverse('profile'))
        else:
            messages.error(request, 'Có lỗi xảy ra. Vui lòng kiểm tra lại thông tin.')
    else:
        form = ProfileUpdateForm(instance=profile)

    return render(request, 'profile_update.html', {'form': form})

# Trang Dashboard
def dashboard(request):
    top_rated_products = Product.objects.annotate(num_reviews=Count('reviews')).order_by('-num_reviews')[:5]
    newest_products = Product.objects.order_by('-updated_at')[:5]
    cheapest_products = Product.objects.order_by('price')[:5]

    context = {
        'top_rated_products': top_rated_products,
        'newest_products': newest_products,
        'cheapest_products': cheapest_products,
    }

    return render(request, 'base.html', context)

# Trang chi tiết sản phẩm
@login_required
def product_detail(request, product_id):
    # Lấy sản phẩm
    product = get_object_or_404(Product, id=product_id)

    # Kiểm tra xem người dùng đã mua sản phẩm chưa
    has_purchased = Order.objects.filter(user=request.user, product=product).exists()

    # Xử lý đánh giá
    if request.method == 'POST':
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            messages.success(request, "Đánh giá của bạn đã được gửi thành công!")
        else:
            messages.error(request, "Có lỗi xảy ra khi gửi đánh giá.")

    # Lấy các đánh giá và tính điểm trung bình
    reviews = product.reviews.all()
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0

    review_form = ReviewForm()

    # Trả về template với dữ liệu sản phẩm và đánh giá
    return render(request, 'product_details.html', {
        'product': product,
        'reviews': reviews,
        'has_purchased': has_purchased,
        'review_form': review_form,
        'average_rating': average_rating,
    })

# Nạp tiền vào tài khoản
@login_required
def add_funds(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        if amount:
            payment = Payment.objects.create(
                user=request.user,
                amount=amount,
                status='pending'  # Trạng thái chờ duyệt
            )
            messages.success(request, "Yêu cầu nạp tiền của bạn đang chờ duyệt.")
            return redirect('profile')
        else:
            messages.error(request, "Vui lòng nhập số tiền hợp lệ.")
    return render(request, 'add_funds.html')

# Xác nhận thanh toán bởi Admin
@login_required
def confirm_payment(request, payment_id):
    if not request.user.is_staff:
        raise Http404("Bạn không có quyền duyệt thanh toán này.")
    
    payment = get_object_or_404(Payment, id=payment_id)
    if payment.status == 'approved':
        messages.warning(request, "Thanh toán này đã được duyệt trước đó.")
        return redirect('admin_dashboard')
    
    if payment.status == 'pending':
        payment.status = 'approved'
        payment.save()

        payment.user.profile.balance += payment.amount
        payment.user.profile.save()

        messages.success(request, f"Thanh toán của người dùng {payment.user.username} đã được duyệt.")
        messages.success(payment.user, f"Bạn đã nạp thành công {payment.amount} VNĐ vào tài khoản của mình.")
        
    return redirect('admin_dashboard')

# Chỉnh sửa bình luận
@login_required
def edit_review(request, id):
    review = get_object_or_404(Review, id=id)
    if review.user != request.user:
        raise Http404("Bạn không có quyền chỉnh sửa bình luận này.")
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, "Chỉnh sửa bình luận thành công!")
            return redirect('product_detail', product_id=review.product.id)
    else:
        form = ReviewForm(instance=review)
    return render(request, 'edit_review.html', {'form': form, 'review': review})

# Xoá bình luận
@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    if review.user != request.user:
        raise Http404("Bạn không có quyền xoá bình luận này.")
    product_id = review.product.id
    review.delete()
    messages.success(request, "Đã xoá bình luận thành công!")
    return redirect('product_detail', product_id=product_id)

# API gửi đánh giá
def submit_rating(request, product_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            rating = data.get("rating")
            if rating is None or not (1 <= rating <= 5):
                return JsonResponse({"status": "error", "message": "Invalid rating value."}, status=400)
            product = Product.objects.get(id=product_id)
            existing_review = Review.objects.filter(user=request.user, product=product).first()
            if existing_review:
                existing_review.rating = rating
                existing_review.save()
                return JsonResponse({"status": "success", "message": "Rating updated successfully."})
            else:
                review = Review(user=request.user, product=product, rating=rating)
                review.save()
                return JsonResponse({"status": "success", "message": "Rating submitted successfully."})
        except Product.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Product not found."}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON data."}, status=400)

# API tạo profile khi đăng ký
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

# Lưu profile khi người dùng cập nhật
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

# Danh sách sản phẩm
def product_list(request):
    products = Product.objects.all()
    return render(request, 'product_list.html', {'products': products})

# Xác nhận mua sản phẩm@@login_required
def confirm_purchase(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    user_profile = request.user.profile
    product_price = product.price

    if Order.objects.filter(user=request.user, product=product).exists():
        return JsonResponse({"status": "error", "message": "Bạn đã mua sản phẩm này rồi."}, status=400)

    if user_profile.balance < product_price:
        return JsonResponse({"status": "error", "message": "Số dư tài khoản không đủ để thanh toán sản phẩm."}, status=400)

    # Return success response to trigger confirmation in the template
    return JsonResponse({"status": "success", "message": "Xác nhận mua hàng thành công."})

# API tìm kiếm sản phẩm
def search_suggestions(request):
    query = request.GET.get('q', '')
    if query:
        products = Product.objects.filter(name__icontains=query)
        suggestions = [{'id': product.id, 'name': product.name} for product in products]
        return JsonResponse(suggestions, safe=False)
    return JsonResponse([], safe=False)

# Trang thư viện
@login_required
def library(request):
    library_items = Library.objects.filter(user=request.user)
    products = [item.product for item in library_items]

    return render(request, 'library.html', {'products': products})

@login_required
def purchase_product(request, product_id):
    if request.method == 'POST':
        try:
            # Đọc dữ liệu từ request
            product = get_object_or_404(Product, id=product_id)
            user_profile = request.user.profile
            product_price = product.price

            # Kiểm tra nếu người dùng đã mua sản phẩm
            if Order.objects.filter(user=request.user, product=product).exists():
                return JsonResponse({"status": "error", "message": "Bạn đã mua sản phẩm này rồi."}, status=400)

            # Kiểm tra số dư tài khoản
            if user_profile.balance < product_price:
                return JsonResponse({"status": "error", "message": "Số dư tài khoản không đủ để thanh toán sản phẩm."}, status=400)

            with transaction.atomic():
                # Tạo đơn hàng
                order = Order.objects.create(user=request.user, product=product, total_price=product_price)

                # Cập nhật trạng thái đơn hàng
                order.status = 'pending'
                order.save()

                # Cập nhật số lượng sản phẩm
                if product.stock > 0:
                    product.stock -= 1
                    product.save()
                else:
                    return JsonResponse({"status": "error", "message": "Sản phẩm đã hết hàng."}, status=400)

                # Thêm sản phẩm vào thư viện của người dùng
                Library.objects.get_or_create(user=request.user, product=product)

                return JsonResponse({"status": "success", "message": "Đơn hàng đã được tạo thành công."})

        except Exception as e:
            return JsonResponse({"status": "error", "message": f"Lỗi: {str(e)}"}, status=500)

    return JsonResponse({"status": "error", "message": "Yêu cầu không hợp lệ."}, status=400)
