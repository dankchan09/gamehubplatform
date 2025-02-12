from django import forms
from .models import Profile
from .models import Review

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['username', 'address', 'age', 'gender', 'avatar', 'bio'] 
avatar = forms.ImageField(required=False)  
bio = forms.CharField(widget=forms.Textarea, required=False)  

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']

class SearchForm(forms.Form):
    query = forms.CharField(max_length=100, required=False, label='Tìm kiếm')


