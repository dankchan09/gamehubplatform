# apps.py
from django.apps import AppConfig

class AccountsConfig(AppConfig):
    name = 'player'  # Thay đổi theo tên ứng dụng của bạn

    def ready(self):
        import player.signals  # Import signals khi ứng dụng khởi động
