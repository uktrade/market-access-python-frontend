from django.forms import Field, Form


def field_to_dict(field: Field, name: str):
    return {
        "type": field.__class__.__name__,
        "widget_type": field.widget.__class__.__name__,
        # "hidden": field.is_hidden,
        "required": field.required,
        "label": field.label,
        "help_text": field.help_text,
        "min_length": getattr(field, "min_length", None),
        "max_length": getattr(field, "max_length", None),
        "initial_value": field.initial,
        "name": name,
        "choices": getattr(field, "choices", None),
    }


def form_fields_to_dict(form: Form):
    form_fields = {}
    for name, field in form.fields.items():
        form_fields[name] = field_to_dict(field, name)
    return form_fields
