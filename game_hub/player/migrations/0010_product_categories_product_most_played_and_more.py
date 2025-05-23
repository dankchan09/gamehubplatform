# Generated by Django 5.1.4 on 2025-01-23 03:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('player', '0009_alter_product_image_alter_profile_age_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='categories',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='product',
            name='most_played',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='product',
            name='trending_game',
            field=models.BooleanField(default=False),
        ),
    ]
