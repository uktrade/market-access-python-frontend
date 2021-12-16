from django import template

register = template.Library()


@register.filter
def completeness_total(barrier):
    total = 0
    if barrier.location:
        total += 10
    if barrier.summary:
        total += 10
    if barrier.source:
        total += 10
    if barrier.categories:
        total += 10
    if barrier.commodities:
        total += 10
    return total
