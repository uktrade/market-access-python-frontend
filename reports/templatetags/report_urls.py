from django import template
from django.urls import reverse


register = template.Library()


@register.simple_tag
def report_stage_url(report_id, stage_code):
    if stage_code == "1.1":
        return reverse('reports:barrier_status')
    elif stage_code == "1.2":
        return reverse('reports:barrier_status')
    elif stage_code == "1.3":
        return reverse('reports:barrier_status')
    elif stage_code == "1.4":
        return reverse('reports:barrier_status')
    elif stage_code == "1.5":
        return reverse('reports:barrier_status')
    return reverse('reports:draft_barriers')
