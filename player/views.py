from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ProfileUpdateForm
from .models import Profile
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .forms import UploadFileForm
from .models import Product



def player(request):
    return render(request, 'base.html')

def shop(request):
    products = Product.objects.all()
    return render(request, 'shop.html', {'products': products})

@login_required
def profile(request):
    return render(request, 'profile.html')

@login_required
def update_profile(request):
    # Ensure the user has a profile, create one if not
    if not hasattr(request.user, 'profile'):
        Profile.objects.create(user=request.user)

    profile = request.user.profile

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cập nhật thông tin thành công!')
            return redirect('profile')
        else:
            messages.error(request, 'Có lỗi xảy ra. Vui lòng kiểm tra lại thông tin.')
    else:
        form = ProfileUpdateForm(instance=profile)

    return render(request, 'profile_update.html', {'form': form})

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('file_upload_success')
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})

def upload_success(request):
    return render(request, 'upload_success.html')

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product_tags = []

    if hasattr(product, 'detail') and product.detail:
        product_tags = product.detail.tags.split(",") if product.detail.tags else []

    return render(request, 'product_details.html', {
        'product': product,
        'product_tags': product_tags,
    })