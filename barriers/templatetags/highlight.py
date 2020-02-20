import re

from django import template
from django.utils.safestring import mark_safe


register = template.Library()


@register.filter(needs_autoescape=True)
def highlight(value, arg, autoescape=True):
    if not arg:
        return value

    result = re.sub(
        fr"({arg})", r"<span class='highlight'>\1</span>", value, flags=re.IGNORECASE
    )

    return mark_safe(result)
