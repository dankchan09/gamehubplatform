from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

# Form đăng ký
class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': _('Nhập email của bạn')}),
        error_messages={'required': _('Vui lòng nhập email.')}
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': _('Nhập tên đăng nhập')}),
        error_messages={'required': _('Vui lòng nhập tên đăng nhập.')}
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': _('Nhập mật khẩu')}),
        error_messages={'required': _('Vui lòng nhập mật khẩu.')}
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': _('Xác nhận mật khẩu')}),
        error_messages={'required': _('Vui lòng xác nhận mật khẩu.')}
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_('Email đã được sử dụng.'))
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_('Mật khẩu không khớp.'))
        return password2

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': _('Nhập tên đăng nhập')}),
        error_messages={'required': _('Vui lòng nhập tên đăng nhập.')}
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': _('Nhập mật khẩu')}),
        error_messages={'required': _('Vui lòng nhập mật khẩu.')}
    )

    error_messages = {
        'invalid_login': _(
            "Tên đăng nhập hoặc mật khẩu không chính xác. Vui lòng thử lại."
        ),
        'inactive': _("Tài khoản này hiện không hoạt động."),
    }
