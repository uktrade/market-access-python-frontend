from django import template

FORM_GROUP_CLASSES = "govuk-form-group"
FORM_GROUP_ERROR_CLASSES = "govuk-form-group--error"

register = template.Library()


@register.simple_tag()
def form_group_classes(*args):
    """Used to set CSS classes for a form group"""
    classes = [FORM_GROUP_CLASSES]
    for arg in args:
        if arg:
            classes.append(FORM_GROUP_ERROR_CLASSES)
    return " ".join(set(classes))


@register.inclusion_tag('partials/form_field_error.html')
def form_field_error(form, field_name):
    error = form.errors.get(field_name)
    return {
        'error': error
    }


def get_custom_errors(errors):
    custom_errors = {}
    for field_name, errors in errors.items():
        for error in errors:
            custom_errors[field_name] = {
                'id': field_name,
                'field_name': field_name.replace("_", " ").title(),
                'text': error,
            }
    return custom_errors


@register.inclusion_tag('partials/forms/error_summary.html')
def form_error_banner(form):
    return {
        'custom_errors': get_custom_errors(form.errors)
    }


@register.filter
def get_field(dictionary, key):
    try:
        return dictionary[key]
    except KeyError:
        return None


@register.filter
def as_text(value):
    value = value.as_text()
    value = value.lstrip("* ")
    return value
