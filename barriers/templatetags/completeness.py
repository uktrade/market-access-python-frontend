from django import template

register = template.Library()


@register.filter
def completeness_total(barrier):
    total = 0
    if barrier.location:
        total += 18
    if barrier.summary:
        total += 18
    if barrier.source:
        total += 16
    if barrier.sectors:
        total += 16
    if barrier.categories:
        total += 16
    if barrier.commodities:
        total += 16
    return total
