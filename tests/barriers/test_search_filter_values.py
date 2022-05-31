from collections import defaultdict
from http import HTTPStatus

from django.forms import MultipleChoiceField
from django.urls import reverse
from html.parser import HTMLParser

from barriers.forms.search import BarrierSearchForm
from core.tests import MarketAccessTestCase
from utils.metadata import get_metadata


class CheckboxFinder(HTMLParser):
    """
    A simple HTML parser that just builds a collection of all the checkboxes on the page
    """

    found_checkboxes = defaultdict(list)

    def handle_starttag(self, tag, attrs) -> None:
        super().handle_starttag(tag, attrs)
        attrs_by_name = {name: value for name, value in attrs}
        if tag == "input" and attrs_by_name["type"] == "checkbox":
            self.found_checkboxes[attrs_by_name["name"]].append(
                {
                    "checked": "checked" in attrs_by_name,
                    "value": attrs_by_name["value"],
                }
            )


class FormValuesCaseInsensitivityTestCase(MarketAccessTestCase):
    """
    This test class examines the BarrierSearchForm for MultipleChoiceFields
    and generates two test methods for each field (except "extra_location" which seems to be unused):
    one test ensures the checkboxes are rendered with identical values to the choices for the field;
    and the other ensures the checkboxes are checked if the corresponding choice value is in the form data.

    This concept could be extended to generate a distinct test for every single choice,
    but that seems like overkill :-)
    """

    metadata = get_metadata()
    form_class = BarrierSearchForm
    parsed_checkboxes = None

    excluded_fields = ["extra_location"]

    @classmethod
    def generate_test_for_checkbox_values_equal_to_choices(cls, field_name):
        def _test(self):
            if self.parsed_checkboxes is None:
                response = self.client.get(
                    reverse("barriers:search"),
                )
                parser = CheckboxFinder()
                parser.feed(response.rendered_content)
                self.parsed_checkboxes = parser.found_checkboxes
            field = self.form.fields[field_name]
            choice_values = [choice[0] for choice in field.choices]
            field_elements = self.parsed_checkboxes[field_name]
            field_element_values = [element["value"] for element in field_elements]
            for choice_value in choice_values:
                assert choice_value in field_element_values

        return _test

    @classmethod
    def generate_test_for_checkbox_checked_when_choice_selected(cls, field_name):
        def _test(self):
            field = self.form.fields[field_name]
            choice_values = [choice[0] for choice in field.choices]
            data = {
                "search": "Test search",
                field_name: choice_values,
            }
            response = self.client.get(
                reverse("barriers:search"),
                data=data,
            )
            assert response.status_code == HTTPStatus.OK
            parser = CheckboxFinder()
            parser.feed(response.rendered_content)
            field_elements = parser.found_checkboxes[field_name]
            field_elements_by_value = {
                element["value"]: element["checked"] for element in field_elements
            }
            for choice_value in choice_values:
                assert choice_value in field_elements_by_value
                assert field_elements_by_value[choice_value]

        return _test

    @classmethod
    def generateTests(cls):
        cls.form = cls.form_class(metadata=cls.metadata, data=None)
        field_names = [
            field_name
            for field_name in cls.form.fields
            if field_name not in cls.excluded_fields
        ]
        for field_name in field_names:
            if isinstance(cls.form.fields[field_name], MultipleChoiceField):
                _test = cls.generate_test_for_checkbox_values_equal_to_choices(
                    field_name
                )
                setattr(cls, f"test_{field_name}_values_equal_to_choices", _test)
                _test = cls.generate_test_for_checkbox_checked_when_choice_selected(
                    field_name
                )
                setattr(cls, f"test_{field_name}_checked_when_choice_selected", _test)


FormValuesCaseInsensitivityTestCase.generateTests()
