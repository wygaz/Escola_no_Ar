from django import template

register = template.Library()


@register.filter
def get_item(mapping, key):
    """Safely get a key from a dict-like object in Django templates.

    Usage:
        {% load vocacional_extras %}
        {{ my_dict|get_item:some_key }}

    Works with int/str keys.
    """
    if mapping is None:
        return None
    try:
        return mapping.get(key)
    except Exception:
        try:
            return mapping.get(str(key))
        except Exception:
            return None
