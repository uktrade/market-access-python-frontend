import datetime
import magic
import os

from django import forms
from django.core.exceptions import ValidationError
from django.forms import widgets
from django.template.defaultfilters import filesizeformat

from .validators import validate_date_not_in_future


class MultipleValueField(forms.MultipleChoiceField):
    """
    Allows multiple values, but is not restricted to values in 'choices'
    """

    def valid_value(self, value):
        return True


class RestrictedFileField(forms.FileField):
    """
    Custom FileField with restrictions on content types and file size
    """

    mime_types = {
        "image/gif": ".gif",
        "image/png": ".png",
        "image/webp": ".webp",
        "image/jpeg": ".jpg",
        "text/csv": ".csv",
        "text/plain": ".txt",
        "application/rtf": ".rtf",
        "application/pdf": ".pdf",
        "application/vnd.oasis.opendocument.text": ".odt",
        "application/msword": ".doc",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
        "application/vnd.oasis.opendocument.presentation": ".odp",
        "application/vnd.ms-powerpoint": ".ppt",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation": ".pptx",
        "application/vnd.oasis.opendocument.spreadsheet": ".ods",
        "application/vnd.ms-excel": ".xls",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
    }

    def __init__(self, *args, **kwargs):
        self.content_types = kwargs.pop("content_types")
        self.max_upload_size = kwargs.pop("max_upload_size")
        super().__init__(*args, **kwargs)

    def get_allowed_extensions(self):
        return [
            self.mime_types.get(content_type) for content_type in self.content_types
        ]

    def clean(self, *args, **kwargs):
        """
        Raise an error if file type or size is not allowed

        Note that the mimetype of csv files will not always be text/csv, so we
        also look at the file extension.
        """
        data = super().clean(*args, **kwargs)

        if not data:
            return

        content_type = magic.from_buffer(data.file.read(), mime=True)
        extension = os.path.splitext(data.name)[1]
        allowed_extensions = self.get_allowed_extensions()

        if (
            content_type not in self.content_types
            and extension not in allowed_extensions
        ):
            raise forms.ValidationError(
                f"Unsupported file format. The following file formats are "
                f"accepted {', '.join(allowed_extensions)}"
            )

        if data.size > self.max_upload_size:
            raise forms.ValidationError(
                f"File size exceeds the {filesizeformat(self.max_upload_size)}"
                " limit. Reduce file size and upload the document again."
            )

        return data


class ChoiceFieldWithHelpText(forms.ChoiceField):
    """
    ChoiceField where help text can be provided for each choice

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


class MonthYearWidget(forms.MultiWidget):
    template_name = "partials/forms/widgets/month_year_widget.html"

    def __init__(self, attrs=None):
        widget = (widgets.NumberInput(), widgets.NumberInput())
        super().__init__(widget, attrs=attrs)

    def decompress(self, value):
        if value:
            return [value.month, value.year]
        return [None, None]


class MonthYearField(forms.MultiValueField):
    widget = MonthYearWidget
    default_validators = [validate_date_not_in_future]

    def __init__(self, **kwargs):
        fields = (
            forms.IntegerField(
                label="Month",
                min_value=1,
                max_value=12,
                error_messages={
                    "min_value": "Please enter a valid month",
                    "max_value": "Please enter a valid month",
                },
            ),
            forms.IntegerField(
                label="Year",
                min_value=1990,
                max_value=2100,
                error_messages={
                    "min_value": "Please enter a valid 4-digit year",
                    "max_value": "Please enter a valid 4-digit year",
                },
            ),
        )
        super().__init__(fields=fields, require_all_fields=True, **kwargs)

    def compress(self, data_list):
        if data_list:
            month, year = data_list
            if month in self.empty_values:
                raise ValidationError(
                    self.error_messages["invalid_month"], code="invalid_month"
                )
            if year in self.empty_values:
                raise ValidationError(
                    self.error_messages["invalid_year"], code="invalid_year"
                )

            return datetime.date(year, month, 1)


class SubformChoiceField(forms.ChoiceField):
    """
    ChoiceField where each choice includes a subform.

    The main form will need to use SubformMixin.

    Example usage:

    reason = SubformChoiceField(
        choices=(
            ("DUPLICATE", "Duplicate"),
            ("NOT_A_BARRIER", "Not a barrier"),
        ),
        subform_classes={
            "DUPLICATE": DuplicateBarrierForm,
            "NOT_A_BARRIER": NotABarrierForm,
        }
    )

    Template snippet:

    {% for choice in form.fields.reason.enhanced_choices %}
      <div class="govuk-radios__item">
        <input name="{{ form.reason.name }}" type="radio" value="{{ choice.value }}">
        <label>{{ choice.name }}</label>
      </div>

      <div id="conditional-{{ choice.value }}">
        {{ choice.subform.as_html }}
      </div>
    {% endfor %}
    """
    subforms = {}

    def __init__(self, *, subform_classes={}, **kwargs):
        super().__init__(**kwargs)
        self.subform_classes = subform_classes

    @property
    def enhanced_choices(self):
        for value, name in self.choices:
            yield {
                "value": value,
                "name": name,
                "subform": self.subforms[value],
            }

    def init_subforms(self, data, selected_value=None):
        for value, subform_class in self.subform_classes.items():
            if value == selected_value:
                subform = subform_class(data)
                self.subform = subform
                self.subforms[value] = subform
            else:
                self.subforms[value] = subform_class()


class SubformMixin:
    """
    A form mixin to be used for forms with SubformChoiceField
    """
    subform_fields = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        data = kwargs.get("data")

        for name, field in self.fields.items():
            if isinstance(field, SubformChoiceField):
                self.subform_fields[name] = field
                field.init_subforms(
                    data=kwargs.get("data"),
                    selected_value=kwargs.get("data", {}).get(name),
                )

    @property
    def errors(self):
        form_errors = super().errors
        if self.is_bound:
            for name, field in self.subform_fields.items():
                if name in self.cleaned_data:
                    form_errors.update(field.subform.errors)
        return form_errors
