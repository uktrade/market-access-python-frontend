from operator import itemgetter
from urllib.parse import urlencode

from django import forms
from django.http import QueryDict

from utils.tools import nested_sort


class BarrierSearchForm(forms.Form):
    edit = forms.IntegerField(required=False, widget=forms.HiddenInput())
    search = forms.CharField(label='Search', max_length=255, required=False)
    country = forms.MultipleChoiceField(
        label='Barrier location',
        required=False,
    )
    sector = forms.MultipleChoiceField(
        label='Sector',
        required=False,
    )
    type = forms.MultipleChoiceField(
        label='Barrier type',
        required=False,
    )
    region = forms.MultipleChoiceField(
        label='Overseas region',
        required=False,
    )
    priority = forms.MultipleChoiceField(
        label='Barrier priority',
        required=False
    )
    status = forms.MultipleChoiceField(
        label='Barrier status',
        required=False
    )
    created_by = forms.MultipleChoiceField(
        label='Show only',
        choices=[
            ('1', 'My barriers'),
            ('2', 'My team barriers'),
        ],
        required=False
    )

    def __init__(self, metadata, *args, **kwargs):
        self.metadata = metadata

        if isinstance(kwargs['data'], QueryDict):
            kwargs['data'] = self.get_data_from_querydict(kwargs['data'])

        super().__init__(*args, **kwargs)
        self.set_country_choices()
        self.set_sector_choices()
        self.set_barrier_type_choices()
        self.set_region_choices()
        self.set_priority_choices()
        self.set_status_choices()

    def get_data_from_querydict(self, data):
        """
        Get form data from the GET parameters.
        """
        cleaned_data = {
            'edit': data.get('edit'),
            'search': data.get('search'),
            'country': data.getlist('country'),
            'sector': data.getlist('sector'),
            'type': data.getlist('type'),
            'region': data.getlist('region'),
            'priority': data.getlist('priority'),
            'status': data.getlist('status'),
            'created_by': data.getlist('created_by'),
        }
        return {k: v for k, v in cleaned_data.items() if v}

    def set_country_choices(self):
        self.fields['country'].choices = [
            ("", "All locations")
        ] + [
            (country['id'], country['name'])
            for country in self.metadata.get_country_list()
        ]

    def set_sector_choices(self):
        self.fields['sector'].choices = [
            ("", "All sectors")
        ] + [
            (sector['id'], sector['name'])
            for sector in self.metadata.get_sector_list(level=0)
        ]

    def set_barrier_type_choices(self):
        choices = [
            (str(barrier_type['id']), barrier_type['title'])
            for barrier_type in self.metadata.data['barrier_types']
        ]
        choices = list(set(choices))
        choices.sort(key=itemgetter(1))
        choices = [("", "All barrier types")] + choices
        self.fields['type'].choices = choices

    def set_region_choices(self):
        choices = [
            (country['id'], country['name'])
            for country in self.metadata.get_overseas_region_list()
        ]
        choices = list(set(choices))
        choices.sort(key=itemgetter(1))
        choices = [("", "All regions")] + choices
        self.fields['region'].choices = choices

    def set_priority_choices(self):
        priorities = self.metadata.data['barrier_priorities']
        priorities.sort(key=itemgetter('order'))
        choices = [
            (
                priority['code'],
                (
                    f"<span class='priority-marker "
                    f"priority-marker--{ priority['code'].lower() }'>"
                    f"</span>{priority['name']}"
                )
            )
            for priority in priorities
        ]
        self.fields['priority'].choices = choices

    def set_status_choices(self):
        status_ids = ('1', '2', '3', '4', '5', '7')
        choices = [
            (id, value)
            for id, value in self.metadata.data['barrier_status'].items()
            if id in status_ids
        ]
        choices.sort(key=itemgetter(0))
        self.fields['status'].choices = choices

    def clean_country(self):
        data = self.cleaned_data['country']
        if "" in data:
            data.remove("")
        return data

    def clean_region(self):
        data = self.cleaned_data['region']
        if "" in data:
            data.remove("")
        return data

    def get_api_search_parameters(self):
        params = {}
        params['text'] = self.cleaned_data.get('search')
        params['location'] = ",".join(
            self.cleaned_data.get('country', [])
            + self.cleaned_data.get('region', [])
        )
        params['sector'] = ",".join(self.cleaned_data.get('sector', []))
        params['barrier_type'] = ",".join(self.cleaned_data.get('type', []))
        params['priority'] = ",".join(self.cleaned_data.get('priority', []))
        params['status'] = ",".join(self.cleaned_data.get('status', []))

        if '1' in self.cleaned_data.get('created_by', []):
            params['user'] = '1'
        elif '2' in self.cleaned_data.get('created_by', []):
            params['team'] = '2'
        return {k: v for k, v in params.items() if v}

    def get_filters_with_values(self):
        return {
            key: value
            for key, value in self.cleaned_data.items()
            if value
        }

    def get_grouped_filters(self):
        """
        Get the currently applied filters grouped by name.

        Looks up the human-friendly value for fields with choices
        and calculates the url to remove each filter.
        """
        filters = {}

        for name, value in self.cleaned_data.items():
            if self.fields[name].widget.is_hidden:
                continue

            remove_params = self.cleaned_data.copy()
            del remove_params[name]

            field = self.fields[name]
            filters[name] = {
                'label': field.label,
                'value': value,
                'remove_url': urlencode(remove_params, doseq=True),
            }
            if hasattr(field, 'choices'):
                field_lookup = dict(field.choices)
                filters[name]['value'] = ", ".join(
                    [field_lookup.get(x) for x in value]
                )

        return filters

    def do_filters_match(self, filters):
        form_filters = self.get_filters_with_values()
        return nested_sort(filters) == nested_sort(form_filters)
