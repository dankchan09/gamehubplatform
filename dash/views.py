from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .forms import RegisterForm, LoginForm
from player.models import Product, PlayerProfile
from django.http import Http404
from django.contrib.auth.models import User  # Đảm bảo rằng User được import đúng

from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login as auth_login

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Kiểm tra xác thực người dùng
            user = authenticate(request, username=username, password=password)

            if user is not None:
                auth_login(request, user)
                user.last_login = timezone.now()
                user.save()
                messages.success(request, 'Đăng nhập thành công!')
                return redirect('player')  # Đảm bảo redirect đến trang chính sau khi đăng nhập
            else:
                # Xử lý lỗi khi không thể xác thực
                form.add_error(None, "Tên đăng nhập hoặc mật khẩu không chính xác. Vui lòng thử lại.")
        else:
            # Nếu form không hợp lệ
            messages.error(request, "Vui lòng kiểm tra lại các thông tin và thử lại.")
    
    else:
        form = AuthenticationForm()

    return render(request, 'dash/login.html', {'form': form})


# Đăng ký
def register(request):
    form = RegisterForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.save()  # Lưu người dùng mới
            try:
                # Kiểm tra xem người dùng đã có profile chưa
                if not hasattr(user, 'playerprofile'):
                    PlayerProfile.objects.create(user=user)
                    messages.success(request, 'Tạo tài khoản thành công! Bạn có thể đăng nhập ngay.')
                else:
                    messages.warning(request, 'Tài khoản đã có profile. Bạn có thể đăng nhập ngay.')
            except Exception as e:
                messages.error(request, f"Lỗi khi tạo profile: {str(e)}")
                print(f"Error: {e}")
            return redirect('login')  # Chuyển hướng tới trang đăng nhập
        else:
            messages.error(request, 'Đăng ký thất bại. Vui lòng kiểm tra thông tin và thử lại.')
    return render(request, 'dash/register.html', {'form': form})

# Trang người chơi
@login_required(login_url='login')  # Chỉ cho phép truy cập khi đã đăng nhập
def player(request):
    return render(request, 'player/base.html')

# Trang cửa hàng
@login_required(login_url='login')  # Chỉ cho phép truy cập khi đã đăng nhập
def shop(request):
    return render(request, 'player/shop.html')

def index(request):
    products = Product.objects.all()
    return render(request, 'dash/guest.html', {
        'products': products  # Chuyển danh sách sản phẩm ra view
    })

def product_detail(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        raise Http404("Sản phẩm không tồn tại.")
    except Exception as e:
        # Xử lý các lỗi khác nếu cần
        messages.error(request, f"Lỗi: {str(e)}")
        return redirect('index')
    
    return render(request, 'product_details.html', {'product': product})
