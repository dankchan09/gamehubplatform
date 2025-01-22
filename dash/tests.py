from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages

class RegisterViewTest(TestCase):
    def test_register_valid_user(self):
        # Đăng ký người dùng hợp lệ
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'Passw0rd@123',
            'password2': 'Passw0rd@123',
        })
        
        # Kiểm tra chuyển hướng sau khi đăng ký thành công
        self.assertRedirects(response, reverse('login'))
        
        # Kiểm tra có thông báo thành công không
        messages = [msg.message for msg in get_messages(response.wsgi_request)]
        self.assertIn('Tạo tài khoản thành công! Bạn có thể đăng nhập ngay.', messages)

    def test_register_existing_email(self):
        # Tạo người dùng đầu tiên
        User.objects.create_user(username='user1', email='user1@example.com', password='Passw0rd@123')
        
        # Đăng ký người dùng với email đã tồn tại
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'user1@example.com',  # Email đã tồn tại
            'password1': 'Passw0rd@123',
            'password2': 'Passw0rd@123',
        })

        # Lấy form từ context và kiểm tra lỗi
        form = response.context['form']
        if form.is_bound:
            self.assertFormError(response, 'form', 'email', 'Email đã được sử dụng.')
        else:
            print(form.errors)

    def test_register_invalid_user(self):
        # Đăng ký người dùng với mật khẩu không khớp
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'Passw0rd@123',
            'password2': 'DifferentPassword@123',  # Mật khẩu không khớp
        })
        
        # Lấy form từ context và kiểm tra lỗi
        form = response.context['form']
        if form.is_bound:
            self.assertFormError(response, 'form', 'password2', 'Mật khẩu không khớp.')
        else:
            print(form.errors)

    def test_login_invalid_user(self):
        # Đăng nhập với thông tin sai
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpassword',
        })
        
        # Lấy form từ context để kiểm tra lỗi
        form = response.context['form']
        if form.is_bound:
            self.assertFormError(response, 'form', 'non_field_errors', 'Thông tin đăng nhập không hợp lệ.')
        else:
            print(form.errors)

    def test_login_valid_user(self):
        # Tạo người dùng hợp lệ
        User.objects.create_user(username='testuser', email='testuser@example.com', password='Passw0rd@123')

        # Đăng nhập với thông tin chính xác
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'Passw0rd@123',
        })
        
        # Kiểm tra chuyển hướng sau khi đăng nhập thành công
        self.assertRedirects(response, reverse('player'))

        # Kiểm tra có thông báo thành công không
        messages = [msg.message for msg in get_messages(response.wsgi_request)]
        self.assertIn('Đăng nhập thành công!', messages)
