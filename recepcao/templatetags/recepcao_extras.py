from django import template


register = template.Library()


@register.filter
def has_group(user, group_name: str) -> bool:
    """Return True if the authenticated user belongs to the given group name."""
    try:
        return bool(user.is_authenticated and user.groups.filter(name=group_name).exists())
    except Exception:
        return False


@register.filter
def startswith(text: str, prefix: str) -> bool:
    try:
        return str(text).startswith(prefix)
    except Exception:
        return False


