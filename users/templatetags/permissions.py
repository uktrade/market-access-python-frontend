from django import template

register = template.Library()


@register.filter
def has_permission(value, arg):
    if value:
        return value.has_permission(arg)
    return False
