# apps.py
from django.apps import AppConfig

class AccountsConfig(AppConfig):
    name = 'player'  

    def ready(self):
        import player.signals  
