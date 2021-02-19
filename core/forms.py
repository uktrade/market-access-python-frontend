import collections
from datetime import date

from django import forms


class SubFormsMixin:
    sub_forms = None

    def get_sub_forms(self):
        return self.sub_forms or {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for k, v in self.get_sub_forms().items():
            f = collections.OrderedDict()
            for kk, vv in v().fields.items():
                self.fields['{}_{}'.format(k, kk)] = vv
                if not self.fields['{}_{}'.format(k, kk)].label:
                    self.fields['{}_{}'.format(k, kk)].label = kk.replace(
                        '_', ' ').title()
                f['{}_{}'.format(k, kk)] = self.fields['{}_{}'.format(k, kk)]

            v_form = v(*args, **kwargs)
            v_form.fields = f
            setattr(self, k, v_form)


class MonthYearForm(forms.Form):
    month = forms.IntegerField(
        label="Month",
        min_value=1,
        max_value=12,
        error_messages={
            "required": "Month is required."
        },
        required=False
    )
    year = forms.IntegerField(
        label="Year",
        min_value=2000,
        max_value=date.today().year,
        error_messages={
            "required": "Year is required."
        },
        required=False
    )
