from barriers.constants import (ACTION_PLAN_TASK_CATEGORIES,
                                ACTION_PLAN_TASK_CHOICES,
                                ACTION_PLAN_TASK_TYPE_CHOICES)
from barriers.forms.mixins import APIFormMixin
from django import forms
from django.forms import ValidationError
from django.template.loader import render_to_string
from django.urls import reverse
from utils.api.client import MarketAccessAPIClient
from utils.forms import (ClearableMixin, MonthYearField, SubformChoiceField,
                         SubformMixin)
from utils.sso import SSOClient
from utils.validators import validate_date_is_in_future


class MonthYearInFutureField(MonthYearField):
    default_validators = []


class ActionPlanMilestoneForm(ClearableMixin, APIFormMixin, forms.Form):

    objective = forms.CharField(
        widget=forms.Textarea(attrs={"class": "govuk-textarea"}),
        label="Add here what is your milestone objective",
        error_messages={"required": "Enter your milestone objective"},
    )

    completion_date = MonthYearInFutureField(
        label="Completion date",
        error_messages={"required": "Enter the completion date"},
    )

    def __init__(self, barrier_id, *args, **kwargs):
        self.barrier_id = barrier_id
        super().__init__(*args, **kwargs)
        # end_date = kwargs.get("initial", {}).get("completion_date")
        # if end_date:
        #     self.fields["completion_date"].label = "Change end date"

    def clean_completion_date(self):
        return self.cleaned_data["completion_date"].isoformat()

    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.action_plans.add_milestone(
            barrier_id=self.barrier_id,
            objective=self.cleaned_data.get("objective"),
            completion_date=self.cleaned_data.get("completion_date"),
        )

    def get_success_url(self):
        return reverse(
            "barriers:action_plan", 
            kwargs={"barrier_id": self.barrier_id}
        )

class ActionPlanMilestoneEditForm(ClearableMixin, APIFormMixin, forms.Form):

    objective = forms.CharField(
        widget=forms.Textarea(attrs={"class": "govuk-textarea"}),
        label="Add here what is your milestone objective",
        error_messages={"required": "Enter your milestone objective"},
    )

    completion_date = MonthYearInFutureField(
        label="Completion date",
        error_messages={"required": "Enter the completion date"},
    )

    def __init__(self, barrier_id, milestone_id, *args, **kwargs):
        self.barrier_id = barrier_id
        self.milestone_id = milestone_id
        super().__init__(*args, **kwargs)

    def clean_completion_date(self):
        return self.cleaned_data["completion_date"].isoformat()

    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.action_plans.edit_milestone(
            barrier_id=self.barrier_id,
            milestone_id=self.milestone_id,
            objective=self.cleaned_data.get("objective"),
            completion_date=self.cleaned_data.get("completion_date"),
        )

    def get_success_url(self):
        return reverse(
            "barriers:action_plan", 
            kwargs={"barrier_id": self.barrier_id}
        )

def get_action_type_category_form(action_type: str):
    field_name = f"action_type_category_{action_type}"

    class ActionPlanActionTypeCategoryForm(forms.Form):

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields[field_name] = forms.ChoiceField(
            label="Select category", choices=ACTION_PLAN_TASK_CATEGORIES[action_type],
        )

        @property
        def get_field(self):
            return self[field_name]

        def get_action_type_category(self):
            return self.cleaned_data[field_name]

        def as_html(self):
            template_name = "barriers/action_plans/action_type_category.html"
            return render_to_string(template_name, context={"form": self})

    return ActionPlanActionTypeCategoryForm


class ActionPlanTaskForm(ClearableMixin, SubformMixin, APIFormMixin, forms.Form):

    status = forms.ChoiceField(
        choices=ACTION_PLAN_TASK_CHOICES, widget=forms.RadioSelect
    )

    start_date = MonthYearInFutureField()
    completion_date = MonthYearInFutureField()

    action_text = forms.CharField(widget=forms.Textarea(attrs={"class": "govuk-textarea"}))

    action_type = SubformChoiceField(
        choices=ACTION_PLAN_TASK_TYPE_CHOICES,
        subform_classes={
            ACTION_PLAN_TASK_TYPE_CHOICES.SCOPING_AND_RESEARCH: get_action_type_category_form(
                "SCOPING_AND_RESEARCH"
            ),
            ACTION_PLAN_TASK_TYPE_CHOICES.LOBBYING: get_action_type_category_form(
                "LOBBYING"
            ),
            ACTION_PLAN_TASK_TYPE_CHOICES.UNILATERAL_INTERVENTIONS: get_action_type_category_form(
                "UNILATERAL_INTERVENTIONS"
            ),
            ACTION_PLAN_TASK_TYPE_CHOICES.BILATERAL_ENGAGEMENT: get_action_type_category_form(
                "BILATERAL_ENGAGEMENT"
            ),
            ACTION_PLAN_TASK_TYPE_CHOICES.PLURILATERAL_ENGAGEMENT: get_action_type_category_form(
                "PLURILATERAL_ENGAGEMENT"
            ),
            ACTION_PLAN_TASK_TYPE_CHOICES.MULTILATERAL_ENGAGEMENT: get_action_type_category_form(
                "MULTILATERAL_ENGAGEMENT"
            ),
            ACTION_PLAN_TASK_TYPE_CHOICES.EVENT: get_action_type_category_form("EVENT"),
            ACTION_PLAN_TASK_TYPE_CHOICES.WHITEHALL_FUNDING_STREAMS: get_action_type_category_form(
                "WHITEHALL_FUNDING_STREAMS"
            ),
            ACTION_PLAN_TASK_TYPE_CHOICES.RESOLUTION_NOT_LEAD_BY_DIT: get_action_type_category_form(
                "RESOLUTION_NOT_LEAD_BY_DIT"
            ),
        },
        widget=forms.RadioSelect,
    )

    assigned_to = forms.CharField(
        widget=forms.TextInput(attrs={"class": "govuk-input"})
    )

    stakeholders = forms.CharField(widget=forms.Textarea(attrs={"class": "govuk-textarea"}))

    def __init__(self, barrier_id, action_plan_id, milestone_id, *args, **kwargs):
        self.barrier_id = barrier_id
        self.action_plan_id = action_plan_id
        self.milestone_id = milestone_id
        super().__init__(*args, **kwargs)

    def clean_start_date(self):
        return self.cleaned_data["start_date"].isoformat()

    def clean_completion_date(self):
        return self.cleaned_data["completion_date"].isoformat()

    def clean_assigned_to(self):
        sso_client = SSOClient()
        query = self.cleaned_data["assigned_to"].replace(".", " ").split("@")[0]
        results = sso_client.search_users(query)
        if not results:
            raise ValidationError(f"Invalid user {query}")
        return results[0]["user_id"]

    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.action_plans.add_task(
            barrier_id=self.barrier_id,
            milestone_id=self.milestone_id,
            assigned_to=self.cleaned_data["assigned_to"],
            status=self.cleaned_data.get("status"),
            action_text=self.cleaned_data.get("action_text"),
            start_date=self.cleaned_data.get("start_date"),
            completion_date=self.cleaned_data.get("completion_date"),
            action_type=self.cleaned_data.get("action_type"),
            action_type_category=self.fields[
                "action_type"
            ].subform.get_action_type_category(),
            stakeholders=self.cleaned_data["stakeholders"]
        )



class ActionPlanTaskEditForm(ClearableMixin, SubformMixin, APIFormMixin, forms.Form):

    status = forms.ChoiceField(
        choices=ACTION_PLAN_TASK_CHOICES, widget=forms.RadioSelect
    )

    start_date = MonthYearInFutureField()
    completion_date = MonthYearInFutureField()

    action_text = forms.CharField(widget=forms.Textarea(attrs={"class": "govuk-textarea"}))

    action_type = SubformChoiceField(
        choices=ACTION_PLAN_TASK_TYPE_CHOICES,
        subform_classes={
            ACTION_PLAN_TASK_TYPE_CHOICES.SCOPING_AND_RESEARCH: get_action_type_category_form(
                "SCOPING_AND_RESEARCH"
            ),
            ACTION_PLAN_TASK_TYPE_CHOICES.LOBBYING: get_action_type_category_form(
                "LOBBYING"
            ),
            ACTION_PLAN_TASK_TYPE_CHOICES.UNILATERAL_INTERVENTIONS: get_action_type_category_form(
                "UNILATERAL_INTERVENTIONS"
            ),
            ACTION_PLAN_TASK_TYPE_CHOICES.BILATERAL_ENGAGEMENT: get_action_type_category_form(
                "BILATERAL_ENGAGEMENT"
            ),
            ACTION_PLAN_TASK_TYPE_CHOICES.PLURILATERAL_ENGAGEMENT: get_action_type_category_form(
                "PLURILATERAL_ENGAGEMENT"
            ),
            ACTION_PLAN_TASK_TYPE_CHOICES.MULTILATERAL_ENGAGEMENT: get_action_type_category_form(
                "MULTILATERAL_ENGAGEMENT"
            ),
            ACTION_PLAN_TASK_TYPE_CHOICES.EVENT: get_action_type_category_form("EVENT"),
            ACTION_PLAN_TASK_TYPE_CHOICES.WHITEHALL_FUNDING_STREAMS: get_action_type_category_form(
                "WHITEHALL_FUNDING_STREAMS"
            ),
            ACTION_PLAN_TASK_TYPE_CHOICES.RESOLUTION_NOT_LEAD_BY_DIT: get_action_type_category_form(
                "RESOLUTION_NOT_LEAD_BY_DIT"
            ),
        },
        widget=forms.RadioSelect,
    )

    assigned_to = forms.CharField(
        widget=forms.TextInput(attrs={"class": "govuk-input"})
    )

    stakeholders = forms.CharField(widget=forms.Textarea(attrs={"class": "govuk-textarea"}))

    def __init__(self, barrier_id, action_plan_id, milestone_id, task_id, *args, **kwargs):
        self.barrier_id = barrier_id
        self.action_plan_id = action_plan_id
        self.milestone_id = milestone_id
        self.task_id = task_id
        super().__init__(*args, **kwargs)

    def clean_start_date(self):
        return self.cleaned_data["start_date"].isoformat()

    def clean_completion_date(self):
        return self.cleaned_data["completion_date"].isoformat()

    def clean_assigned_to(self):
        sso_client = SSOClient()
        query = self.cleaned_data["assigned_to"].replace(".", " ").split("@")[0]
        results = sso_client.search_users(query)
        if not results:
            raise ValidationError(f"Invalid user {query}")
        return results[0]["user_id"]

    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.action_plans.edit_task(
            barrier_id=self.barrier_id,
            task_id=self.task_id,
            assigned_to=self.cleaned_data["assigned_to"],
            status=self.cleaned_data.get("status"),
            action_text=self.cleaned_data.get("action_text"),
            start_date=self.cleaned_data.get("start_date"),
            completion_date=self.cleaned_data.get("completion_date"),
            action_type=self.cleaned_data.get("action_type"),
            action_type_category=self.fields[
                "action_type"
            ].subform.get_action_type_category(),
            stakeholders=self.cleaned_data["stakeholders"]
        )
