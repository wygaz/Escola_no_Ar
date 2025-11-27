# vocacional_sprint_addons/apps/vocacional/templatetags/consent_tags
from django import template
from apps.vocacional.models_consent import Consentimento

register = template.Library()

@register.filter
def consentimento_ativo(user):
    if not user.is_authenticated:
        return False
    return Consentimento.objects.filter(user=user, ativo=True).exists()
