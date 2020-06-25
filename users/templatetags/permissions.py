from django import template

register = template.Library()


@register.filter
def has_permission(value, arg):
    return value.has_permission(arg)
