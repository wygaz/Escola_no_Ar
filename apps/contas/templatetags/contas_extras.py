from django import template
register = template.Library()


@register.filter
def display_name(user):
    return (getattr(user, "first_name", "") or getattr(user, "nome", "") or getattr(user, "email", "")).strip()