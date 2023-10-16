import dateutil.parser
import datetime
from django import forms
from django.forms import widgets
from django.conf import settings

class CommodityCodeWidget(forms.MultiWidget):
    template_name = "partials/forms/widgets/commodity_code_widget.html"
    box_count = 5

    def __init__(self, attrs=None):
        widget = (widgets.TextInput(),) * self.box_count
        super().__init__(widget, attrs=attrs)

    def decompress(self, value):
        if value:
            pairs = [value[i : i + 2] for i in range(0, len(value), 2)]
            pairs += [""] * self.box_count
            return pairs[: self.box_count]
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


class MonthYearWidget(forms.MultiWidget):
    template_name = "partials/forms/widgets/month_year_widget.html"

    def __init__(self, attrs=None, date_range_direction="", help_text=""):
        widget = (widgets.NumberInput(), widgets.NumberInput())
        super().__init__(widget, attrs=attrs)
        self.date_range_direction = date_range_direction
        self.help_text = help_text

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

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["widget"]["date_range_direction"] = self.date_range_direction
        context["widget"]["help_text"] = self.help_text
        return context


class DateRangeWidget(forms.MultiWidget):
    now = datetime.datetime.now()

    def __init__(self, attrs=None):
        from_help_text = f"Example, 04 {self.now.year-2}"
        to_help_text = f"Example, 04 {self.now.year-1}"

        widgets = [
            MonthYearWidget(attrs=attrs, date_range_direction="from", help_text=from_help_text),
            MonthYearWidget(attrs=attrs, date_range_direction="to", help_text=to_help_text),
        ]
        super().__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            from_date, to_date = value.split(",")
            from_date = from_date.split("-")
            to_date = to_date.split("-")

            return [[from_date[1], from_date[0]], [to_date[1], to_date[0]]]
        return [[None, None], [None, None]]

    def format_output(self, rendered_widgets):
        return "-".join(rendered_widgets)

    def value_from_datadict(self, data, files, name):
        if name in data:
            return self.decompress(data.get(name))
        return super().value_from_datadict(data, files, name)
