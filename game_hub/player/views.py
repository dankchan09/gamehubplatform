from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Avg
from django.http import JsonResponse, Http404, FileResponse
from .models import Profile, Product, Review, Payment, Order, Library
from .forms import ProfileUpdateForm, ReviewForm
import json
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.urls import reverse
from django.db import transaction
from django.contrib.auth import logout
from django.conf import settings
import os
from django.http import JsonResponse


def format_vnd(value):
    return f"{value:,} VNĐ"


@login_required
def profile(request):
    return render(request, 'profile.html', {'profile': request.user.profile})

@login_required(login_url='dash:login')
def update_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

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

from django.db.models import Avg, Count

def dashboard(request):
    category_choices = dict(Product.CATEGORY_CHOICES)  # Lấy danh sách thể loại
    products = Product.objects.annotate(
        avg_rating=Avg('reviews__rating'),  # Tính điểm đánh giá trung bình
        review_count=Count('reviews')  # Đếm số lượng đánh giá
    )  # Lấy tất cả sản phẩm và thêm rating vào
    
    return render(request, 'base.html', {
        'category_choices': category_choices,
        'products': products,
    })

def category_view(request, category_key):
    valid_categories = dict(Product.CATEGORY_CHOICES).keys()
    if category_key not in valid_categories:
        return JsonResponse({'error': 'Danh mục không hợp lệ'}, status=400)

    products = Product.objects.filter(category=category_key).annotate(
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    )

    # Chuẩn bị dữ liệu trả về
    products_data = [{
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'avg_rating': product.avg_rating,
        'review_count': product.review_count,
        'image_url': product.image.url if product.image else None,
    } for product in products]

    return JsonResponse({'products': products_data})


@login_required(login_url='dash:login')
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    user_profile = request.user.profile  
    has_purchased = Library.objects.filter(user=request.user, product=product).exists()

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
    else:
        review_form = ReviewForm()

    reviews = product.reviews.all()
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    
    if average_rating is None:
        average_rating = 0
    
    return render(request, 'product_details.html', {
        'product': product,
        'reviews': reviews,
        'has_purchased': has_purchased,
        'review_form': review_form,
        'average_rating': average_rating,
    })

@login_required
def add_funds(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        if amount:
            payment = Payment.objects.create(
                user=request.user,
                amount=amount,
                status='pending'  
            )
            messages.success(request, "Yêu cầu nạp tiền của bạn đang chờ duyệt.")
            return redirect('profile')
        else:
            messages.error(request, "Vui lòng nhập số tiền hợp lệ.")
    return render(request, 'add_funds.html')

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
        messages.success(payment.user, f"Bạn đã nạp thành công {payment.amount} VNĐ vào tài khoản!.")
        
    return redirect('admin_dashboard')

def edit_review(request, review_id):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            review = get_object_or_404(Review, id=review_id)

            if review.user != request.user:
                return JsonResponse({'success': False, 'error': 'Bạn không có quyền chỉnh sửa bình luận này.'}, status=403)

            if request.content_type == "application/json":
                data = json.loads(request.body)
            else:
                data = request.POST

            new_comment = data.get('comment', '').strip()

            if new_comment:
                review.comment = new_comment
                review.save()
                return JsonResponse({'success': True, 'message': 'Bình luận đã được cập nhật.'})
            else:
                return JsonResponse({'success': False, 'error': 'Comment không được rỗng.'}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Dữ liệu không hợp lệ.'}, status=400)

    return JsonResponse({'success': False, 'error': 'Yêu cầu không hợp lệ.'}, status=400)
@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    if review.user != request.user:
        raise Http404("Bạn không có quyền xoá bình luận này.")
    product_id = review.product.id
    review.delete()
    messages.success(request, "Đã xoá bình luận thành công!")
    return redirect('product_detail', product_id=product_id)

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

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

def product_list(request):
    products = Product.objects.all()
    return render(request, 'product_list.html', {'products': products})

@login_required
def confirm_purchase(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    user_profile = request.user.profile
    product_price = product.price

    if Order.objects.filter(user=request.user, product=product).exists():
        return JsonResponse({"status": "error", "message": "Bạn đã mua sản phẩm này rồi."}, status=400)

    if user_profile.balance < product_price:
        return JsonResponse({"status": "error", "message": "Số dư tài khoản không đủ để thanh toán sản phẩm."}, status=400)

    return JsonResponse({"status": "success", "message": "Xác nhận mua hàng thành công."})

def search_suggestions(request):
    query = request.GET.get('q', '')
    if query:
        products = Product.objects.filter(name__icontains=query)[:5]
        suggestions = [{'id': product.id, 'name': product.name} for product in products]
        return JsonResponse(suggestions, safe=False)
    return JsonResponse([], safe=False)

@login_required
def library(request):
    library_items = Library.objects.filter(user=request.user).select_related('product')
    products = [item.product for item in library_items]

    return render(request, 'library.html', {'products': products})

@login_required
def purchase_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    user_profile = request.user.profile
    product_price = product.price

    if Library.objects.filter(user=request.user, product=product).exists():
        messages.error(request, "Bạn đã sở hữu sản phẩm này.")
        return redirect('product_detail', product_id=product.id)

    if user_profile.balance < product_price:
        messages.error(request, "Số dư không đủ!")
        return redirect('product_detail', product_id=product.id)

    if product.stock <= 0:
        messages.error(request, "Sản phẩm đã hết hàng!")
        return redirect('product_detail', product_id=product.id)

    with transaction.atomic():
        order = Order.objects.create(user=request.user, product=product, total_price=product_price, status='completed')

        product.stock -= 1
        product.save()

        user_profile.balance -= product_price
        user_profile.save()

        Library.objects.get_or_create(user=request.user, product=product)

    messages.success(request, "Mua hàng thành công! Sản phẩm đã được thêm vào thư viện.")

    # Kiểm tra nếu game có file để tải
    if product.game_file:
        game_file_path = os.path.join(settings.MEDIA_ROOT, str(product.game_file))
        if os.path.exists(game_file_path):
            return FileResponse(open(game_file_path, 'rb'), as_attachment=True, filename=os.path.basename(game_file_path))
        else:
            messages.error(request, "Lỗi: File game không tồn tại!")
    
    return redirect('product_detail', product_id=product.id)



def user_logout(request):
    logout(request)  
    messages.success(request, "Bạn đã đăng xuất thành công!")  
    return redirect('index')  

def index(request):
    top_rated_products = Product.objects.annotate(num_reviews=Count('reviews')).order_by('-num_reviews')[:5]
    newest_products = Product.objects.order_by('-updated_at')[:5]
    cheapest_products = Product.objects.order_by('price')[:5]
    
    return render(request, 'dash/guest.html', {
        'top_rated_products': top_rated_products,
        'newest_products': newest_products,
        'cheapest_products': cheapest_products,
    })


def download_game(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if product.game_file:  # Kiểm tra xem game có file không
        game_file_path = os.path.join(settings.MEDIA_ROOT, str(product.game_file))
        if os.path.exists(game_file_path):
            return FileResponse(open(game_file_path, 'rb'), as_attachment=True, filename=os.path.basename(game_file_path))
        else:
            messages.error(request, "Lỗi: File game không tồn tại!")
    else:
        messages.error(request, "Lỗi: Sản phẩm này không có file game!")

    return redirect('library')  # Chuyển hướng về thư viện nếu có lỗi