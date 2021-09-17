from django import template

register = template.Library()


@register.filter
def calculation_to_percentage(value: str, decimal_places: int = 10):
    """
    We assume value of 1 is 100%
    """
    normalized_value = float(value) * 100
    if normalized_value < 1 / (10 ** decimal_places):
        return "0%"
    return f"{normalized_value:5f}%"
