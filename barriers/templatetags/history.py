from django import template
from django.template.loader import select_template

register = template.Library()


@register.simple_tag()
def history_item(item):
    template_name = f"barriers/history/partials/{item.model}/{item.field}.html"
    default_template_name = "barriers/history/partials/default.html"
    item_template = select_template([template_name, default_template_name])
    return item_template.render({"item": item})
