# Generated by Django 5.1.4 on 2025-02-20 15:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('player', '0032_rename_full_name_profile_username'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='game_file',
            field=models.FileField(blank=True, null=True, upload_to='game_files/'),
        ),
    ]
