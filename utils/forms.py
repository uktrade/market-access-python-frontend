import datetime
import magic

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
        'image/gif': '.gif',
        'image/png': '.png',
        'image/webp': '.webp',
        'image/jpeg': '.jpg',
        'text/csv': '.csv',
        'text/plain': '.txt',
        'application/rtf': '.rtf',
        'application/pdf': '.pdf',
        'application/msword': '.doc',
        'application/vnd.ms-excel': '.xls',
    }

    def __init__(self, *args, **kwargs):
        self.content_types = kwargs.pop("content_types")
        self.max_upload_size = kwargs.pop("max_upload_size")
        super().__init__(*args, **kwargs)

    def get_allowed_types(self):
        return [
            self.mime_types.get(content_type)
            for content_type in self.content_types
        ]

    def clean(self, *args, **kwargs):
        data = super().clean(*args, **kwargs)

        if not data:
            return

        content_type = magic.from_buffer(data.file.read(), mime=True)

        if content_type not in self.content_types:
            allowed_types = self.get_allowed_types()
            raise forms.ValidationError(
                f"Unsupported file format. The following file formats are "
                f"accepted {', '.join(allowed_types)}"
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
            forms.IntegerField(label="Month", min_value=1, max_value=12),
            forms.IntegerField(label="Year", min_value=2000, max_value=2100),
        )
        super().__init__(
            error_messages={
                'incomplete': (
                    'Enter resolution date and include a month and year.'
                ),
            },
            fields=fields,
            require_all_fields=True,
            **kwargs
        )

    def compress(self, data_list):
        if data_list:
            month, year = data_list
            if month in self.empty_values:
                raise ValidationError(
                    self.error_messages['invalid_month'],
                    code='invalid_month'
                )
            if year in self.empty_values:
                raise ValidationError(
                    self.error_messages['invalid_year'],
                    code='invalid_year'
                )

            return datetime.date(year, month, 1)
