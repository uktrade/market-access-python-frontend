from django import template
from django.template.loader import get_template


register = template.Library()


@register.simple_tag(takes_context=True)
def activity_item(context, item):
    template_name = f"barriers/activity/partials/{item.model}/{item.field}.html"
    try:
        item_template = get_template(template_name)
    except template.TemplateDoesNotExist:
        return ""
    return item_template.render(context.flatten())
