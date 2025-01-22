from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

# Form đăng ký
class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': _('Nhập email của bạn')})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        error_messages = {
            'password2': {
                'password_mismatch': _('Mật khẩu không khớp.')
            },
            'username': {
                'required': _('Vui lòng nhập tên người dùng.')
            },
            'email': {
                'required': _('Vui lòng nhập email.')
            }
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_('Email đã được sử dụng.'))
        return email

# Form đăng nhập
class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': _('Nhập tên đăng nhập')}),
        error_messages={'required': _('Vui lòng nhập tên đăng nhập.')}
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': _('Nhập mật khẩu')}),
        error_messages={'required': _('Vui lòng nhập mật khẩu.')}
    )
