from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"     # ← exatamente isso
    # label = "core"       # (opcional; se definir, use “core” mesmo)