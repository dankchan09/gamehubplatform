from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.utils import timezone
from .forms import RegisterForm, LoginForm

# Trang chủ
def index(request):
    return render(request, 'dash/guest.html')

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)  # Sử dụng `request` và `data` khi tạo form
        if form.is_valid():
            user = form.get_user()  # Hàm get_user sẽ lấy người dùng hợp lệ từ form
            auth_login(request, user)
            user.last_login = timezone.now()
            user.save()
            messages.success(request, 'Đăng nhập thành công!')
            return redirect('player')  # Sau khi đăng nhập, chuyển hướng đến trang người chơi
        else:
            # Log lỗi để kiểm tra form errors chi tiết
            print(f"Form errors: {form.errors}")  # Log lỗi để kiểm tra
            messages.error(request, 'Thông tin đăng nhập không hợp lệ.')
    else:
        form = LoginForm()

    return render(request, 'dash/login.html', {'form': form})

# Đăng ký
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Tạo tài khoản thành công! Bạn có thể đăng nhập ngay.')
            return redirect('login')  # Đảm bảo chuyển hướng tới trang login sau khi đăng ký thành công
        else:
            # In lỗi chi tiết để kiểm tra lý do tại sao form không hợp lệ
            print(form.errors)  # Kiểm tra lý do tại sao form không hợp lệ
            messages.error(request, 'Có lỗi xảy ra. Vui lòng kiểm tra lại thông tin của bạn.')
    else:
        form = RegisterForm()

    return render(request, 'dash/register.html', {'form': form})

# Trang người chơi
def player(request):
    return render(request, 'player/base.html')

# Trang cửa hàng
def shop(request):
    return render(request, 'player/shop.html')
