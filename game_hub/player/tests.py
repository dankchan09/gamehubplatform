from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Profile, Product, Order, Library, Payment
from django.contrib.messages import get_messages


class ProfileViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client = Client()
        self.client.login(username='testuser', password='password')

    def test_profile_view(self):
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')
        self.assertContains(response, 'Cập nhật thông tin')  

    def test_update_profile(self):
        response = self.client.get(reverse('profile_update'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile_update.html')

    def test_update_profile_post(self):
        response = self.client.post(reverse('profile_update'), {'first_name': 'Updated Name'})
        self.assertRedirects(response, reverse('profile'))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Cập nhật thông tin thành công!')


class ProductDetailViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.product = Product.objects.create(name='Game A', price=500, stock=10)
        self.client = Client()
        self.client.login(username='testuser', password='password')

    def test_product_detail_view(self):
        response = self.client.get(reverse('product_detail', args=[self.product.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'product_details.html')
        self.assertContains(response, self.product.name)

    def test_product_review_submission(self):
        review_data = {'rating': 5, 'comment': 'Great product!'}
        response = self.client.post(reverse('product_detail', args=[self.product.id]), review_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Đánh giá của bạn đã được gửi thành công!')


class AddFundsViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client = Client()
        self.client.login(username='testuser', password='password')

    def test_add_funds_get(self):
        response = self.client.get(reverse('add_funds'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'add_funds.html')

    def test_add_funds_post_success(self):
        response = self.client.post(reverse('add_funds'), {'amount': 1000})
        self.assertRedirects(response, reverse('profile'))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Yêu cầu nạp tiền của bạn đang chờ duyệt.')

    def test_add_funds_post_fail(self):
        response = self.client.post(reverse('add_funds'), {'amount': ''})
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Vui lòng nhập số tiền hợp lệ.')


class ConfirmPurchaseViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.product = Product.objects.create(name='Game A', price=500, stock=10)
        self.client = Client()
        self.client.login(username='testuser', password='password')

    def test_confirm_purchase_success(self):
        response = self.client.post(reverse('confirm_purchase', args=[self.product.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Xác nhận mua hàng thành công.')

    def test_confirm_purchase_insufficient_balance(self):
        self.user.profile.balance = 100
        self.user.profile.save()
        response = self.client.post(reverse('confirm_purchase', args=[self.product.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Số dư tài khoản không đủ để thanh toán sản phẩm.')


class LibraryViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client = Client()
        self.client.login(username='testuser', password='password')

    def test_library_view(self):
        response = self.client.get(reverse('library'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'library.html')


class SearchSuggestionsViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.product1 = Product.objects.create(name='Game A', price=500, stock=10)
        self.product2 = Product.objects.create(name='Game B', price=300, stock=15)

    def test_search_suggestions(self):
        response = self.client.get(reverse('search_suggestions') + '?q=Game')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Game A')
        self.assertContains(response, 'Game B')


class LogoutViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client = Client()
        self.client.login(username='testuser', password='password')

    def test_logout_view(self):
        response = self.client.get(reverse('user_logout'))
        self.assertRedirects(response, reverse('index'))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Bạn đã đăng xuất thành công!')
