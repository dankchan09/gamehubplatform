from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Avg
from django.http import JsonResponse, Http404
from .models import Profile, Product, Review, Payment
from .forms import ProfileUpdateForm, ReviewForm
import json
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

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
            return redirect('profile')
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
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = Review.objects.filter(product=product)

    # Tính điểm đánh giá trung bình
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0

    if request.method == 'POST' and 'review_id' not in request.POST:
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            return redirect('product_detail', product_id=product.id)
    else:
        review_form = ReviewForm()

    if request.method == 'POST' and 'add_to_cart' in request.POST:
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
            cart.products.add(product)
            return redirect('cart')
        else:
            return redirect('login')

    return render(request, 'product_details.html', {
        'product': product,
        'reviews': reviews,
        'average_rating': average_rating,
        'review_form': review_form,
    })

@login_required
def payment(request):
    # Assuming we want to get a list of selected products from the URL or another method.
    product_ids = request.POST.getlist('product_ids')  # You can adjust this based on how products are passed to the view
    products = Product.objects.filter(id__in=product_ids)

    if not products:
        return redirect('product_list')

    total_price = sum([product.price for product in products])

    if request.method == 'POST':
        payment = Payment.objects.create(
            user=request.user,
            amount=total_price,
            status='pending'
        )
        return redirect('confirm_payment', payment_id=payment.id)

    return render(request, 'payment.html', {'total_price': total_price, 'products': products})

# Xác nhận thanh toán
@login_required
def confirm_payment(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    user_profile = request.user.profile

    if user_profile.balance >= payment.amount:
        user_profile.balance -= payment.amount
        user_profile.save()

        payment.status = 'completed'
        payment.save()

        user_profile.purchased_products.add(*payment.cart.products.all())
        
        return redirect('payment_complete')

    return redirect('payment')

# Hoàn tất thanh toán
@login_required
def payment_complete(request):
    return render(request, 'payment_complete.html')

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

# Tìm kiếm sản phẩm
def search_suggestions(request):
    query = request.GET.get('q', '')
    if query:
        products = Product.objects.filter(name__icontains=query)
        suggestions = [{'id': product.id, 'name': product.name} for product in products]
        return JsonResponse(suggestions, safe=False)
    return JsonResponse([], safe=False)

# API tạo profile khi đăng ký
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

# Lưu profile khi người dùng cập nhật
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

def product_list(request):
    products = Product.objects.all()
    return render(request, 'product_list.html', {'products': products})