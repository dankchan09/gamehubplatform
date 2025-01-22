from django import forms
from .models import Profile
from .models import UploadFile


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['full_name', 'address', 'age', 'gender', 'avatar', 'bio'] # Các trường cần cập nhật']
avatar = forms.ImageField(required=False)  # Nếu có ảnh đại diện mới
bio = forms.CharField(widget=forms.Textarea, required=False)  # Cập nhật mô tả

class UploadFileForm(forms.ModelForm):
    class Meta:
        model = UploadFile
        fields = ['title', 'file']
