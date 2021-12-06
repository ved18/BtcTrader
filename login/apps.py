from django.apps import AppConfig
from . import scheeduler

class LoginConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'login'

    def ready(self):
        scheeduler.start()
 

