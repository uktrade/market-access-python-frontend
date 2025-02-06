import re

from django import template
from django.utils.html import format_html

register = template.Library()


@register.filter(needs_autoescape=True)
def highlight_mentions(value, user_email=None, autoescape=True):
    regex = r"(@[^ @]+@[^ @\r\n]+)"
    def wrap_email(match):
        email = match.group(1)
        if user_email and email == "@" + user_email:
            return (
                f"<span class='mention-highlight mention-highlight__me'>{email}</span>"
            )
        return f"<span class='mention-highlight'>{email}</span>"
    result = re.sub(regex, wrap_email, value, 0, re.MULTILINE)
    return format_html(result)


@register.filter(needs_autoescape=True)
def get_mention_emails(value, user_email=None, autoescape=True):

    regex = r"(@[^ @]+@[^ @\r\n]+)"

    def wrap_email(match):
        email = match.group(1)[1:]  # Remove leading @ for a clean email value
        return f"{email},"

    result = re.sub(regex, wrap_email, value, 0, re.MULTILINE)

    return result.split(",")[:-1]
