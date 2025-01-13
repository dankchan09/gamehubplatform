from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login as auth_login



# Trang chủ
def home(request):
    return render(request, 'dash/home.html')

def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)  # Đảm bảo gọi đúng login từ django.contrib.auth
            return redirect('home')  # Chuyển hướng đến trang Home (URL name)
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'dash/login.html')

def register(request):
    return render(request, 'dash/register.html')
