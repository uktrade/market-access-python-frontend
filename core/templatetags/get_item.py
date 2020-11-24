from django import template

register = template.Library()


@register.filter
def get_item(obj, key):
    if key in obj:
        return obj[key]
