from django import template
register = template.Library()

@register.simple_tag(takes_context=True)
def nav_active(context, prefix: str):
    path = context["request"].path
    return "is-active" if path.startswith(prefix) else ""
