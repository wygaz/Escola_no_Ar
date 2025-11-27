# apps/core/signals.py
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from .models import claim_pending_access

@receiver(user_logged_in)
def conciliar_acessos_pendentes(sender, request, user, **kwargs):
    try:
        claim_pending_access(user)
    except Exception:
        # Evita quebrar login em caso de erro; logue se quiser
        pass
