from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User
from django.utils import timezone
from .models import RegisterForm  # Đảm bảo rằng bạn đã tạo một form đăng ký đúng

# Trang chủ
def home(request):
    return render(request, 'dash/home.html')

# Đăng nhập
def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Đăng nhập người dùng vào session
            auth_login(request, user)

            # Lưu thông tin vào database (cập nhật thời gian đăng nhập cuối cùng)
            user.last_login = timezone.now()  # Lưu thời gian đăng nhập
            user.save()  # Lưu thay đổi vào cơ sở dữ liệu

            # Thêm thông báo thành công
            messages.success(request, "Login successful. Welcome back!")

            # Chuyển hướng đến trang home
            return redirect('home')  # Điều hướng đến trang home
        else:
            messages.error(request, "Invalid username or password.")
    
    return render(request, 'dash/login.html')

# Đăng ký
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # Lưu tài khoản vào cơ sở dữ liệu
            user = form.save()
            messages.success(request, 'Account created successfully! You can now log in.')

            # Sau khi đăng ký thành công, chuyển hướng đến trang login
            return redirect('login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RegisterForm()  # Nếu là GET, khởi tạo form trống

    return render(request, 'dash/register.html', {'form': form})
