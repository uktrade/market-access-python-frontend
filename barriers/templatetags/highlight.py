import re

from django import template
from django.utils.html import format_html

register = template.Library()


@register.filter(needs_autoescape=True)
def highlight(value, arg, autoescape=True):
    if not arg:
        return value

    result = re.sub(
        rf"({arg})", r"<span class='highlight'>\1</span>", value, flags=re.IGNORECASE
    )

    return format_html(result)
