from django import template


register = template.Library()


@register.simple_tag
def report_stage_url(urls, stage_code):
    return urls.get(stage_code, "")
