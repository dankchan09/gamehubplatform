from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages

class RegisterViewTest(TestCase):
    def test_register_valid_user(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'Passw0rd@123',
            'password2': 'Passw0rd@123',
        })
        
        self.assertRedirects(response, reverse('login'))  # Kiểm tra chuyển hướng thành công

        # Kiểm tra thông báo hiển thị
        messages = [msg.message for msg in get_messages(response.wsgi_request)]
        self.assertIn('Tạo tài khoản thành công! Bạn có thể đăng nhập ngay.', messages)

    def test_register_existing_email(self):
        User.objects.create_user(username='user1', email='user1@example.com', password='Passw0rd@123')
        
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'user1@example.com',             'password1': 'Passw0rd@123',
            'password2': 'Passw0rd@123',
        })

        self.assertEqual(response.status_code, 200)  
        self.assertContains(response, 'Email đã được sử dụng.')

    def test_register_invalid_user(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'Passw0rd@123',
            'password2': 'DifferentPassword@123', 
        })
        
        # Kiểm tra rằng form đã được ràng buộc và hiển thị lỗi chính xác
        self.assertEqual(response.status_code, 200)  # Form sẽ hiển thị lại với mã 200
        self.assertContains(response, 'Mật khẩu không khớp.')

    def test_login_invalid_user(self):
        # Đăng nhập với thông tin không hợp lệ
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpassword',
        })
        
        self.assertEqual(response.status_code, 200)  # Form sẽ hiển thị lại với mã 200
        self.assertContains(response, 'Thông tin đăng nhập không hợp lệ.')

    def test_login_valid_user(self):
        # Tạo người dùng hợp lệ
        User.objects.create_user(username='testuser', email='testuser@example.com', password='Passw0rd@123')

        # Đăng nhập với thông tin hợp lệ
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'Passw0rd@123',
        })
        
        # Kiểm tra chuyển hướng đến trang "player"
        self.assertRedirects(response, reverse('player'))

        # Kiểm tra thông báo hiển thị
        messages = [msg.message for msg in get_messages(response.wsgi_request)]
        self.assertIn('Đăng nhập thành công!', messages)
