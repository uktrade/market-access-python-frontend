from operator import itemgetter

from django import forms


class BarrierSearchForm(forms.Form):
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
        super().__init__(*args, **kwargs)
        self.set_country_choices()
        self.set_sector_choices()
        self.set_barrier_type_choices()
        self.set_region_choices()
        self.set_priority_choices()
        self.set_status_choices()

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
        if self.is_valid():
            params['text'] = self.cleaned_data['search']
            params['location'] = ",".join(
                self.cleaned_data['country']
                + self.cleaned_data['region']
            )
            params['sector'] = ",".join(self.cleaned_data['sector'])
            params['barrier_type'] = ",".join(self.cleaned_data['type'])
            params['priority'] = ",".join(self.cleaned_data['priority'])
            params['status'] = ",".join(self.cleaned_data['status'])

            if '1' in self.cleaned_data['created_by']:
                params['user'] = '1'
            elif '2' in self.cleaned_data['created_by']:
                params['team'] = '2'
            params = {k: v for k, v in params.items() if v}
        return params
