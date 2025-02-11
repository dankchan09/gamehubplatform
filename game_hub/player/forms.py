from django import forms
from .models import Profile
from .models import Review

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['username', 'address', 'age', 'gender', 'avatar', 'bio'] # Các trường cần cập nhật']
avatar = forms.ImageField(required=False)  # Nếu có ảnh đại diện mới
bio = forms.CharField(widget=forms.Textarea, required=False)  # Cập nhật mô tả

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']

class SearchForm(forms.Form):
    query = forms.CharField(max_length=100, required=False, label='Tìm kiếm')


