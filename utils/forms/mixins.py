class SubformMixin:
    """
    A form mixin to be used for forms with SubformChoiceField
    """

    subform_fields = {}

    def __init__(self, *args, **kwargs):
        from utils.forms.fields import SubformChoiceField

        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            if isinstance(field, SubformChoiceField):
                if "data" in kwargs:
                    selected_value = kwargs.get("data", {}).get(name)
                else:
                    selected_value = kwargs.get("initial", {}).get(name)
                self.subform_fields[name] = field
                field.init_subforms(
                    selected_value=selected_value,
                    **kwargs,
                )

    @property
    def errors(self):
        form_errors = super().errors
        if self.is_bound:
            for name, field in self.subform_fields.items():
                if name in self.cleaned_data and hasattr(field, "subform"):
                    form_errors.update(field.subform.errors)
        return form_errors


class ClearableMixin:
    """
    Bypass form validation if 'clear' button was pressed
    """

    def _clean_fields(self):
        if "clear" not in self.data:
            return super()._clean_fields()


class HelpTextMixin:
    """
    Allow ChoiceFields to include help text for each choice

    choices should be a three part tuple (value, name, help_text)
    """

    def valid_value(self, value):
        """Check to see if the provided value is a valid choice."""
        text_value = str(value)
        for k, v, help_text in self.choices:
            if isinstance(v, (list, tuple)):
                # This is an optgroup, so look inside the group for options
                for k2, v2 in v:
                    if value == k2 or text_value == str(k2):
                        return True
            else:
                if value == k or text_value == str(k):
                    return True
        return False
