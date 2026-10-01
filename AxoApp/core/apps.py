from django.apps import AppConfig


class CoreConfig(AppConfig):    #Definieren der Konfiguration der App
    default_auto_field = 'django.db.models.BigAutoField' #Datentyp für auto generierte Primärschlüssel
    name = 'core'
