import re

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(needs_autoescape=True)
def highlight_mentions(value, autoescape=True):

    regex = r"(@[^ @]+@[^ @]+)"

    result = re.sub(regex, r"<span class='mention-highlight'>\1</span>", value, 0, re.MULTILINE)

    return mark_safe(result)
