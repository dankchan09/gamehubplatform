# Generated by Django 5.1.4 on 2025-01-28 14:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('player', '0011_game_delete_uploadfile'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='status',
            field=models.CharField(choices=[('pending', 'Chờ xét duyệt'), ('approved', 'Đã duyệt'), ('rejected', 'Từ chối')], default='pending', max_length=10),
        ),
    ]
