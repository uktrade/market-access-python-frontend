from django import template

register = template.Library()


@register.simple_tag
def report_stage_url(urls, stage_code):
    return urls.get(stage_code, "")


@register.simple_tag
def equal_boolean(a, b):
    if isinstance(a, str):
        left_val = True if a == "True" else False
    else:
        left_val = a
    if isinstance(b, str):
        right_val = True if b == "True" else False
    else:
        right_val = b
    return "checked" if left_val == right_val else ""
