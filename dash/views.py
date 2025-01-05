from django.http import HttpResponse
from django.shortcuts import render

def home(request):
    return render(request, 'dash/home.html')

def guest(request):
    return render(request, 'dash/guest.html')

def register(request):
    return render(request, 'dash/register.html')

def login(request):
    return render(request, 'dash/login.html')

def login_process(request):
    if request.method == "POST":
        # Xử lý đăng nhập ở đây
        username = request.POST.get('username')
        password = request.POST.get('password')
        # Giả lập xử lý
        if username == "admin" and password == "password123":
            return HttpResponse("Login successful!")
        else:
            return HttpResponse("Invalid credentials!", status=401)
    return HttpResponse("Only POST method is allowed.", status=405)