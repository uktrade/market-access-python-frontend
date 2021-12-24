from django import template

register = template.Library()


@register.filter
def completeness_total(barrier):
    """
    Returns the completeness percentage of a given barrier.
    18% for location being provided
    18% for a summary being provided
    16% for the source of information being provided
    16% for the sectors affected being provided
    16% for the barrier categories being provided
    16% for the commodities affected being provided
    """
    total = 0
    if barrier.location:
        total += 18
    if barrier.summary:
        total += 18
    if barrier.source:
        total += 16
    if hasattr(barrier, "sectors") and barrier.sectors:
        total += 16
    if hasattr(barrier, "categories") and barrier.categories:
        total += 16
    if hasattr(barrier, "commodities") and barrier.commodities:
        total += 16
    return total
