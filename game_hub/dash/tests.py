import unittest
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .forms import RegisterForm, LoginForm
from player.models import PlayerProfile, Product, Library

class RegisterFormTest(TestCase):
    def test_register_form_valid(self):
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'Testpassword123!',
            'password2': 'Testpassword123!'
        }
        form = RegisterForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_register_form_invalid_email(self):
        form_data = {
            'username': 'testuser',
            'email': 'invalid-email',
            'password1': 'Testpassword123!',
            'password2': 'Testpassword123!'
        }
        form = RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

class LoginViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='Testpassword123!')
    
    def test_login_valid(self):
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'Testpassword123!'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['user'].is_authenticated)
    
    def test_login_invalid(self):
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'wrongpassword'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['user'].is_authenticated)

class ProductTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='Testpassword123!')
        self.product = Product.objects.create(name='Test Product', price=10.0)
        self.client.login(username='testuser', password='Testpassword123!')
    
    def test_product_detail(self):
        response = self.client.get(reverse('product_detail', args=[self.product.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Product')

if __name__ == '__main__':
    unittest.main()
