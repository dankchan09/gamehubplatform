from django.contrib import admin
from .models import Product
from .models import ProductDetail
# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'discount_price')
    search_fields = ('name', 'category')
    list_filter = ('category',)

class ProductDetailAdmin(admin.ModelAdmin):
    list_display = ('product', 'additional_info', 'tags')
    search_fields = ('product__name', 'tags')

admin.site.register(Product, ProductAdmin)
admin.site.register(ProductDetail, ProductDetailAdmin)