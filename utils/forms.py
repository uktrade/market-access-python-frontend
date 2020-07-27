import datetime
import magic
import os

from django import forms
from django.core.exceptions import ValidationError
from django.forms import widgets
from django.template.defaultfilters import filesizeformat

from .validators import validate_date_not_in_future

import dateutil.parser


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
        self.multi_document = kwargs.pop("multi_document", True)
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


class ChoiceFieldWithHelpText(HelpTextMixin, forms.ChoiceField):
    pass


class MultipleChoiceFieldWithHelpText(HelpTextMixin, forms.MultipleChoiceField):
    pass


class YesNoBooleanField(forms.ChoiceField):
    """
    Display a BooleanField as Yes and No radio buttons
    """

    def __init__(self, **kwargs):
        choices = (
            ("yes", "Yes"),
            ("no", "No"),
        )
        super().__init__(choices=choices, **kwargs)

    def prepare_value(self, data):
        if data is True:
            return "yes"
        elif data is False:
            return "no"
        return data

    def to_python(self, value):
        if value == "yes":
            return True
        elif value == "no":
            return False

    def valid_value(self, value):
        value = self.prepare_value(value)
        return super().valid_value(value)


class MonthYearWidget(forms.MultiWidget):
    template_name = "partials/forms/widgets/month_year_widget.html"

    def __init__(self, attrs=None):
        widget = (widgets.NumberInput(), widgets.NumberInput())
        super().__init__(widget, attrs=attrs)

    def decompress(self, value):
        if value:
            if isinstance(value, str):
                try:
                    value = dateutil.parser.parse(value)
                except ValueError:
                    return [None, None]
            return [value.month, value.year]
        return [None, None]

    def value_from_datadict(self, data, files, name):
        if name in data:
            return self.decompress(data.get(name))
        return super().value_from_datadict(data, files, name)


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
                    "min_value": "Enter a real month",
                    "max_value": "Enter a real month",
                    "incomplete": "Enter a month",
                },
            ),
            forms.IntegerField(
                label="Year",
                min_value=1990,
                max_value=2100,
                error_messages={
                    "min_value": "Enter a real year",
                    "max_value": "Enter a real year",
                    "incomplete": "Enter a year",
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


class DayMonthYearWidget(forms.MultiWidget):
    template_name = "partials/forms/widgets/day_month_year_widget.html"

    def __init__(self, attrs=None):
        widget = (widgets.NumberInput(), widgets.NumberInput(), widgets.NumberInput())
        super().__init__(widget, attrs=attrs)

    def decompress(self, value):
        if value:
            if isinstance(value, str):
                try:
                    value = dateutil.parser.parse(value)
                except ValueError:
                    return [None, None, None]
            return [value.day, value.month, value.year]
        return [None, None, None]

    def value_from_datadict(self, data, files, name):
        if name in data:
            return self.decompress(data.get(name))
        return super().value_from_datadict(data, files, name)


class DayMonthYearField(forms.MultiValueField):
    widget = DayMonthYearWidget
    default_error_messages = {
        "required": "Enter a day, month and year",
        "invalid": "Enter a real date",
    }

    def __init__(self, **kwargs):
        fields = (
            forms.IntegerField(
                label="Day",
                min_value=1,
                max_value=31,
                error_messages={
                    "min_value": "Enter a real day",
                    "max_value": "Enter a real day",
                    "incomplete": "Enter a day",
                },
            ),
            forms.IntegerField(
                label="Month",
                min_value=1,
                max_value=12,
                error_messages={
                    "min_value": "Enter a real month",
                    "max_value": "Enter a real month",
                    "incomplete": "Enter a month",
                },
            ),
            forms.IntegerField(
                label="Year",
                min_value=1990,
                max_value=2100,
                error_messages={
                    "min_value": "Enter a real year",
                    "max_value": "Enter a real year",
                    "incomplete": "Enter a year",
                },
            ),
        )
        super().__init__(fields=fields, require_all_fields=False, **kwargs)

    def compress(self, data_list):
        if data_list:
            day, month, year = data_list
            if day in self.empty_values:
                raise ValidationError(
                    self.error_messages["invalid_day"], code="invalid_day"
                )
            if month in self.empty_values:
                raise ValidationError(
                    self.error_messages["invalid_month"], code="invalid_month"
                )
            if year in self.empty_values:
                raise ValidationError(
                    self.error_messages["invalid_year"], code="invalid_year"
                )

            try:
                return datetime.date(year, month, day)
            except ValueError:
                raise ValidationError(self.error_messages["invalid"], code="invalid")


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

    def __init__(self, *, subform_classes={}, choices_help_text={}, **kwargs):
        super().__init__(**kwargs)
        self.subform_classes = subform_classes
        self.choices_help_text = choices_help_text

    @property
    def enhanced_choices(self):
        for value, name in self.choices:
            choice = {
                "value": value,
                "name": name,
            }
            if value in self.subforms:
                choice["subform"] = self.subforms[value]
            if value in self.choices_help_text:
                choice["help_text"] = self.choices_help_text[value]
            yield choice

    def init_subforms(self, initial, data, selected_value=None):
        for value, subform_class in self.subform_classes.items():
            if value == selected_value:
                subform = subform_class(initial=initial, data=data)
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

        for name, field in self.fields.items():
            if isinstance(field, SubformChoiceField):
                if "data" in kwargs:
                    selected_value = kwargs.get("data", {}).get(name)
                else:
                    selected_value = kwargs.get("initial", {}).get(name)
                self.subform_fields[name] = field
                field.init_subforms(
                    initial=kwargs.get("initial"),
                    data=kwargs.get("data"),
                    selected_value=selected_value,
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


class CommodityCodeWidget(forms.MultiWidget):
    template_name = "partials/forms/widgets/commodity_code_widget.html"
    box_count = 5

    def __init__(self, attrs=None):
        widget = (widgets.TextInput(), ) * self.box_count
        super().__init__(widget, attrs=attrs)

    def decompress(self, value):
        if value:
            pairs = [value[i:i+2] for i in range(0, len(value), 2)]
            pairs += [""] * self.box_count
            return pairs[:self.box_count]
        return [""] * self.box_count

    def value_from_datadict(self, data, files, name):
        if data.get(name):
            return data.get(name)
        values = super().value_from_datadict(data, files, name)
        formatted_values = []
        has_values = False
        for value in reversed(values):
            if has_values or value:
                has_values = True
                formatted_values.insert(0, value.zfill(2))
        return "".join(formatted_values)
