# Generated by Django 5.1.4 on 2025-01-21 06:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('player', '0008_product_updated_at_alter_product_category_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(default='products/default.jpg', upload_to='products/'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='age',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='avatar',
            field=models.ImageField(default='avatars/default.jpg', upload_to='avatars/'),
        ),
    ]
