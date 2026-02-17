# apps/vocacional/templatetags/consent_tags.py
from django import template
from apps.vocacional.models_consent import Consentimento

register = template.Library()

@register.filter
def consentimento_ativo(user):
    if not user.is_authenticated:
        return False
    return Consentimento.objects.filter(user=user, aceito=True, revogado_em__isnull=True).exists()
