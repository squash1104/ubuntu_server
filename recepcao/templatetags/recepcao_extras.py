from django import template

register = template.Library()


@register.filter
def has_group(user, group_name: str) -> bool:
    """Return True if the authenticated user belongs to the given group name."""
    try:
        return bool(
            user.is_authenticated and user.groups.filter(name=group_name).exists()
        )
    except Exception:
        return False


@register.filter
def startswith(text: str, prefix: str) -> bool:
    try:
        return str(text).startswith(prefix)
    except Exception:
        return False


@register.filter
def duration_format(start_time, end_time):
    """Calculate and format duration between two datetime objects."""
    try:
        if not start_time or not end_time:
            return "-"

        # Calculate duration
        duration = end_time - start_time
        total_seconds = int(duration.total_seconds())

        if total_seconds < 0:
            return "-"

        # Convert to hours, minutes, seconds
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        if hours > 0:
            return f"{hours:02d}h{minutes:02d}m{seconds:02d}s"
        if minutes > 0:
            return f"{minutes:02d}m{seconds:02d}s"
        return f"{seconds:02d}s"
    except Exception:
        return "-"


@register.filter
def fmt_td(td):
    """Format timedelta object to HHhMMm format."""
    try:
        if not td:
            return "00h00m"
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours:02d}h{minutes:02d}m"
    except Exception:
        return "00h00m"
