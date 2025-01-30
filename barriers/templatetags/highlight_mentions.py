import re

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(needs_autoescape=True)
def get_mention_emails(value, user_email=None, autoescape=True):

    regex = r"(@[^ @]+@[^ @\r\n]+)"

    def wrap_email(match):
        email = match.group(1)[1:]  # Remove leading @ for a clean email value
        return f"{email},"

    result = re.sub(regex, wrap_email, value, 0, re.MULTILINE)

    return result.split(",")[:-1]
