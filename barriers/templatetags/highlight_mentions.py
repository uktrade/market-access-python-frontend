import re

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(needs_autoescape=True)
def highlight_mentions(value, user_email=None, autoescape=True):

    regex = r"(@[^ @]+@[^ @\r\n]+)"

    def wrap_email(match):
        email = match.group(1)
        if user_email and email == "@" + user_email:
            return f"<span class='mention-highlight mention-highlight__me'>{email}</span>"
        return f"<span class='mention-highlight'>{email}</span>"

    result = re.sub(
        regex, wrap_email, value, 0, re.MULTILINE
    )

    return mark_safe(result)
