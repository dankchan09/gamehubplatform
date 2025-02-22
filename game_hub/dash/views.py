from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .forms import RegisterForm
from player.models import Product, PlayerProfile
from django.db.models import Count
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import render, redirect, get_object_or_404
from player.models import Product, PlayerProfile, Library
from player.forms import ReviewForm
from django.db.models import Avg
from django.http import JsonResponse

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)

            if user is not None:
                auth_login(request, user)
                user.last_login = timezone.now()
                user.save()
                messages.success(request, 'Đăng nhập thành công!')
                return redirect('dashboard')  
            else:
                form.add_error(None, "Tên đăng nhập hoặc mật khẩu không chính xác. Vui lòng thử lại.")
        else:
            messages.error(request, "Vui lòng kiểm tra lại các thông tin và thử lại.")
    
    else:
        form = AuthenticationForm()

    return render(request, 'dash/login.html', {'form': form})


# Đăng ký
def register(request):
    form = RegisterForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.save()  
            try:
                if not hasattr(user, 'playerprofile'):
                    PlayerProfile.objects.create(user=user)
                    messages.success(request, 'Tạo tài khoản thành công! Bạn có thể đăng nhập ngay.')
                else:
                    messages.warning(request, 'Tài khoản đã có profile. Bạn có thể đăng nhập ngay.')
            except Exception as e:
                messages.error(request, f"Lỗi khi tạo profile: {str(e)}")
                print(f"Error: {e}")
            return redirect('login')  
        else:
            messages.error(request, 'Đăng ký thất bại. Vui lòng kiểm tra thông tin và thử lại.')
    return render(request, 'dash/register.html', {'form': form})


def index(request):
    category_choices = dict(Product.CATEGORY_CHOICES)  # Lấy danh sách thể loại
    products = Product.objects.annotate(
        avg_rating=Avg('reviews__rating'),  # Tính điểm đánh giá trung bình
        review_count=Count('reviews')  # Đếm số lượng đánh giá
    )  # Lấy tất cả sản phẩm và thêm rating vào
    
    return render(request, 'dash/guest.html', {
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


def product_list(request):
    products = Product.objects.all()
    return render(request, 'player/product_list.html', {'products': products})

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
