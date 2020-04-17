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


@register.inclusion_tag('partials/forms/field_error.html')
def form_field_error(arg1, arg2=None):
    if arg2 is None:
        field = arg1
        return {"errors": field.errors}

    form = arg1
    field_name = arg2
    return {"errors": form.errors.get(field_name)}


def get_custom_errors(errors):
    custom_errors = {}
    for field_name, errors in errors.items():
        for error in errors:
            custom_errors.setdefault(field_name, [])
            custom_errors[field_name].append({
                'id': field_name,
                'field_name': field_name.replace("_", " ").title(),
                'text': error,
            })
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
