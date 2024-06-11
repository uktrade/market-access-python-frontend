import datetime
import logging
import os

import magic
from django import forms
from django.core.exceptions import ValidationError
from django.template.defaultfilters import filesizeformat

from utils.forms.mixins import HelpTextMixin
from utils.forms.widgets import DateRangeWidget, DayMonthYearWidget, MonthYearWidget
from utils.validators import validate_date_not_in_future

logger = logging.getLogger(__name__)


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
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": (
            ".docx"
        ),
        "application/vnd.oasis.opendocument.presentation": ".odp",
        "application/vnd.ms-powerpoint": ".ppt",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation": (
            ".pptx"
        ),
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
                f"The selected file must be a {', '.join(allowed_extensions)}"
            )

        if data.size > self.max_upload_size:
            raise forms.ValidationError(
                f"The selected file must be smaller than {filesizeformat(self.max_upload_size)}"
            )

        return data


class ChoiceFieldWithHelpText(HelpTextMixin, forms.ChoiceField):
    pass


class MultipleChoiceFieldWithHelpText(HelpTextMixin, forms.MultipleChoiceField):
    pass


class YesNoBooleanField(forms.ChoiceField):
    """
    Display a BooleanField as Yes and No radio buttons
    """

    default_choices = (
        ("yes", "Yes"),
        ("no", "No"),
    )

    def __init__(self, choices=None, **kwargs):
        if not choices:
            choices = self.default_choices
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


class TrueFalseBooleanField(forms.NullBooleanField):
    """
    Well Django doesn't have a BooleanField that only accepts True or False!
    This is a Form Field that only accepts True or False.
    """

    def clean(self, value):
        if (value == "True") or (value is True):
            return True
        elif (value == "False") or (value is False):
            return False
        if self.required:
            raise ValidationError("This field is required.")
        return super().clean(value)


class YesNoDontKnowBooleanField(YesNoBooleanField):
    default_choices = (
        ("yes", "Yes"),
        ("no", "No"),
        ("dontknow", "Don't know"),
    )

    def clean(self, value):
        self.validate(value)
        value = self.to_python(value)
        self.run_validators(value)
        return value


class YesNoReviewLaterBooleanField(YesNoBooleanField):
    default_choices = (
        ("yes", "Yes"),
        ("no", "No"),
        ("review_later", "Review later"),
    )

    def clean(self, value):
        self.validate(value)
        value = self.to_python(value)
        self.run_validators(value)
        return value


class DayMonthYearField(forms.MultiValueField):
    widget = DayMonthYearWidget
    default_error_messages = {
        "required": "Enter a day, month and year",
        "invalid": "Enter a real date",
    }
    default_validators = [validate_date_not_in_future]

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

    def init_subforms(self, selected_value=None, **kwargs):
        for value, subform_class in self.subform_classes.items():
            if value == selected_value:
                subform = subform_class(**kwargs)
                self.subform = subform
                self.subforms[value] = subform
            else:
                self.subforms[value] = subform_class(**kwargs)


class MonthYearField(forms.MultiValueField):
    widget = MonthYearWidget
    default_validators = [validate_date_not_in_future]

    def __init__(self, date_range_direction="", **kwargs):
        fields = (
            forms.IntegerField(
                label="Month",
                min_value=1,
                max_value=12,
                error_messages={
                    "min_value": "Enter a date in the format 01 2023",
                    "max_value": "Enter a date in the format 01 2023",
                    "incomplete": "Enter a month",
                    "invalid_month": "Enter a date in the format 01 2023",
                },
            ),
            forms.IntegerField(
                label="Year",
                min_value=1990,
                max_value=2100,
                error_messages={
                    "min_value": "Date must be after 1990",
                    "max_value": "Date must be before 2100",
                    "incomplete": "Enter a year",
                    "invalid_year": "Enter a date in the format 01 2023",
                },
            ),
        )
        self.date_range_direction = date_range_direction
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


class MonthYearInFutureField(MonthYearField):
    default_validators = []


class MonthDateRangeField(forms.MultiValueField):
    widget = DateRangeWidget

    def __init__(self, *args, **kwargs):
        fields = [
            MonthYearInFutureField(),
            MonthYearInFutureField(),
        ]
        super().__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        """As per the Django docs, we do not implement a clean() method here. compress() is used instead and is called
        in the parent's clean method, so ValidationError is handled correctly."""
        if data_list and all(data_list):
            start_date, end_date = data_list
            if start_date and end_date and end_date <= start_date:
                raise forms.ValidationError(
                    "The end date must be after the start date."
                )
            return f"{start_date.strftime('%Y-%m-%d')},{end_date.strftime('%Y-%m-%d')}"
