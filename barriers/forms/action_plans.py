from barriers.constants import (ACTION_PLAN_RAG_STATUS_CHOICES,
                                ACTION_PLAN_TASK_CATEGORIES,
                                ACTION_PLAN_TASK_CHOICES,
                                ACTION_PLAN_TASK_TYPE_CHOICES)
from barriers.forms.mixins import APIFormMixin
from django import forms
from django.forms import ValidationError
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from utils.api.client import MarketAccessAPIClient
from utils.forms import (ClearableMixin, MonthYearField, SubformChoiceField,
                         SubformMixin)
from utils.sso import SSOClient


class MonthYearInFutureField(MonthYearField):
    default_validators = []


class ActionPlanCurrentStatusEditForm(ClearableMixin, APIFormMixin, forms.Form):

    current_status = forms.CharField(
        widget=forms.Textarea(attrs={"class": "govuk-textarea"}),
        label="Add the latest progress update",
        required=False,
    )
    status = forms.ChoiceField(
        label="Action plan delivery confidence",
        choices=ACTION_PLAN_RAG_STATUS_CHOICES,
        widget=forms.RadioSelect,
    )

    def __init__(self, barrier_id, *args, **kwargs):
        self.barrier_id = barrier_id
        super().__init__(*args, **kwargs)

    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.action_plans.edit_action_plan(
            barrier_id=self.barrier_id,
            current_status=self.cleaned_data.get("current_status"),
            current_status_last_updated=timezone.now().isoformat(),
            status=self.cleaned_data.get("status"),
        )

    def get_success_url(self):
        return reverse("barriers:action_plan", kwargs={"barrier_id": self.barrier_id})


class ActionPlanStrategicContextForm(ClearableMixin, APIFormMixin, forms.Form):

    strategic_context = forms.CharField(
        widget=forms.Textarea(attrs={"class": "govuk-textarea"}),
        label="Strategic context",
        required=False,
    )

    def __init__(self, barrier_id, *args, **kwargs):
        self.barrier_id = barrier_id
        super().__init__(*args, **kwargs)

    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.action_plans.edit_action_plan(
            barrier_id=self.barrier_id,
            strategic_context=self.cleaned_data.get("strategic_context"),
        )

    def get_success_url(self):
        return reverse("barriers:action_plan", kwargs={"barrier_id": self.barrier_id})


class ActionPlanMilestoneForm(ClearableMixin, APIFormMixin, forms.Form):

    objective = forms.CharField(
        widget=forms.TextInput(attrs={"class": "govuk-input"}),
        label="Describe the objective",
        error_messages={"required": "Enter your milestone objective"},
    )

    def __init__(self, barrier_id, *args, **kwargs):
        self.barrier_id = barrier_id
        super().__init__(*args, **kwargs)

    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.action_plans.add_milestone(
            barrier_id=self.barrier_id, objective=self.cleaned_data.get("objective"),
        )

    def get_success_url(self):
        return reverse("barriers:action_plan", kwargs={"barrier_id": self.barrier_id})


class ActionPlanMilestoneEditForm(ClearableMixin, APIFormMixin, forms.Form):

    objective = forms.CharField(
        widget=forms.TextInput(attrs={"class": "govuk-input"}),
        label="Describe the objective",
        error_messages={"required": "Enter your milestone objective"},
    )

    def __init__(self, barrier_id, milestone_id, *args, **kwargs):
        self.barrier_id = barrier_id
        self.milestone_id = milestone_id
        super().__init__(*args, **kwargs)

    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.action_plans.edit_milestone(
            barrier_id=self.barrier_id,
            milestone_id=self.milestone_id,
            objective=self.cleaned_data.get("objective"),
        )

    def get_success_url(self):
        return reverse("barriers:action_plan", kwargs={"barrier_id": self.barrier_id})


def action_plan_action_type_category_form_class_factory(action_type: str):
    field_name = f"action_type_category_{action_type}"

    class ActionPlanActionTypeCategoryForm(forms.Form):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields[field_name] = forms.ChoiceField(
                label="Select category",
                choices=ACTION_PLAN_TASK_CATEGORIES[action_type],
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

    action_text = forms.CharField(
        label="Intervention text",
        widget=forms.Textarea(attrs={"class": "govuk-textarea"}),
    )

    action_type = SubformChoiceField(
        label="Intervention type",
        choices=ACTION_PLAN_TASK_TYPE_CHOICES,
        subform_classes={
            ACTION_PLAN_TASK_TYPE_CHOICES.SCOPING_AND_RESEARCH: action_plan_action_type_category_form_class_factory(
                "SCOPING_AND_RESEARCH"
            ),
            ACTION_PLAN_TASK_TYPE_CHOICES.LOBBYING: action_plan_action_type_category_form_class_factory(
                "LOBBYING"
            ),
            ACTION_PLAN_TASK_TYPE_CHOICES.UNILATERAL_INTERVENTIONS: action_plan_action_type_category_form_class_factory(
                "UNILATERAL_INTERVENTIONS"
            ),
            ACTION_PLAN_TASK_TYPE_CHOICES.BILATERAL_ENGAGEMENT: action_plan_action_type_category_form_class_factory(
                "BILATERAL_ENGAGEMENT"
            ),
            ACTION_PLAN_TASK_TYPE_CHOICES.PLURILATERAL_ENGAGEMENT: action_plan_action_type_category_form_class_factory(
                "PLURILATERAL_ENGAGEMENT"
            ),
            ACTION_PLAN_TASK_TYPE_CHOICES.MULTILATERAL_ENGAGEMENT: action_plan_action_type_category_form_class_factory(
                "MULTILATERAL_ENGAGEMENT"
            ),
            ACTION_PLAN_TASK_TYPE_CHOICES.EVENT: action_plan_action_type_category_form_class_factory(
                "EVENT"
            ),
            ACTION_PLAN_TASK_TYPE_CHOICES.WHITEHALL_FUNDING_STREAMS: action_plan_action_type_category_form_class_factory(  # noqa
                "WHITEHALL_FUNDING_STREAMS"
            ),
            ACTION_PLAN_TASK_TYPE_CHOICES.RESOLUTION_NOT_LEAD_BY_DIT: action_plan_action_type_category_form_class_factory(  # noqa
                "RESOLUTION_NOT_LEAD_BY_DIT"
            ),
        },
        widget=forms.RadioSelect,
    )

    assigned_to = forms.CharField(
        widget=forms.TextInput(attrs={"class": "govuk-input"})
    )

    stakeholders = forms.CharField(
        required=True,
        label="Stakeholders",
        widget=forms.Textarea(attrs={"class": "govuk-textarea"}),
    )

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
        email = self.cleaned_data["assigned_to"]
        query = email.replace(".", " ").split("@")[0]
        results = sso_client.search_users(query)
        if not results:
            raise ValidationError(f"Invalid user {query}")
        for result in results:
            if result["email"] == email:
                return result["user_id"]
        return

    def save(self):
        client = MarketAccessAPIClient(self.token)

        action_type_field = self.fields["action_type"]
        if hasattr(action_type_field, "subform"):
            action_type_category = action_type_field.subform.get_action_type_category()
        else:
            action_type_category = "Other"

        client.action_plans.add_task(
            barrier_id=self.barrier_id,
            milestone_id=self.milestone_id,
            assigned_to=self.cleaned_data["assigned_to"],
            status=self.cleaned_data.get("status"),
            action_text=self.cleaned_data.get("action_text"),
            start_date=self.cleaned_data.get("start_date"),
            completion_date=self.cleaned_data.get("completion_date"),
            action_type=self.cleaned_data.get("action_type"),
            action_type_category=action_type_category,
            stakeholders=self.cleaned_data["stakeholders"],
        )


class ActionPlanTaskEditForm(ClearableMixin, SubformMixin, APIFormMixin, forms.Form):

    status = forms.ChoiceField(
        choices=ACTION_PLAN_TASK_CHOICES, widget=forms.RadioSelect
    )

    start_date = MonthYearInFutureField()
    completion_date = MonthYearInFutureField()

    action_text = forms.CharField(
        label="Purpose of the intervention",
        widget=forms.Textarea(attrs={"class": "govuk-textarea"}),
    )

    action_type = SubformChoiceField(
        label="Intervention type",
        choices=ACTION_PLAN_TASK_TYPE_CHOICES,
        subform_classes={
            ACTION_PLAN_TASK_TYPE_CHOICES.SCOPING_AND_RESEARCH: action_plan_action_type_category_form_class_factory(
                "SCOPING_AND_RESEARCH"
            ),
            ACTION_PLAN_TASK_TYPE_CHOICES.LOBBYING: action_plan_action_type_category_form_class_factory(
                "LOBBYING"
            ),
            ACTION_PLAN_TASK_TYPE_CHOICES.UNILATERAL_INTERVENTIONS: action_plan_action_type_category_form_class_factory(
                "UNILATERAL_INTERVENTIONS"
            ),
            ACTION_PLAN_TASK_TYPE_CHOICES.BILATERAL_ENGAGEMENT: action_plan_action_type_category_form_class_factory(
                "BILATERAL_ENGAGEMENT"
            ),
            ACTION_PLAN_TASK_TYPE_CHOICES.PLURILATERAL_ENGAGEMENT: action_plan_action_type_category_form_class_factory(
                "PLURILATERAL_ENGAGEMENT"
            ),
            ACTION_PLAN_TASK_TYPE_CHOICES.MULTILATERAL_ENGAGEMENT: action_plan_action_type_category_form_class_factory(
                "MULTILATERAL_ENGAGEMENT"
            ),
            ACTION_PLAN_TASK_TYPE_CHOICES.EVENT: action_plan_action_type_category_form_class_factory(
                "EVENT"
            ),
            ACTION_PLAN_TASK_TYPE_CHOICES.WHITEHALL_FUNDING_STREAMS: action_plan_action_type_category_form_class_factory(  # noqa
                "WHITEHALL_FUNDING_STREAMS"
            ),
            ACTION_PLAN_TASK_TYPE_CHOICES.RESOLUTION_NOT_LEAD_BY_DIT: action_plan_action_type_category_form_class_factory(  # noqa
                "RESOLUTION_NOT_LEAD_BY_DIT"
            ),
        },
        widget=forms.RadioSelect,
    )

    assigned_to = forms.CharField(
        widget=forms.TextInput(attrs={"class": "govuk-input"})
    )

    stakeholders = forms.CharField(
        label="Stakeholders",
        widget=forms.Textarea(attrs={"class": "govuk-textarea"}),
        required=True,
    )

    def __init__(
        self, barrier_id, action_plan_id, milestone_id, task_id, *args, **kwargs
    ):
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
        email = self.cleaned_data["assigned_to"]
        query = email.replace(".", " ").split("@")[0]
        results = sso_client.search_users(query)
        if not results:
            raise ValidationError(f"Invalid user {query}")
        for result in results:
            if result["email"] == email:
                return result["user_id"]
        return

    def save(self):
        client = MarketAccessAPIClient(self.token)

        action_type_field = self.fields["action_type"]
        if hasattr(action_type_field, "subform"):
            action_type_category = action_type_field.subform.get_action_type_category()
        else:
            action_type_category = "Other"

        client.action_plans.edit_task(
            barrier_id=self.barrier_id,
            task_id=self.task_id,
            assigned_to=self.cleaned_data["assigned_to"],
            status=self.cleaned_data.get("status"),
            action_text=self.cleaned_data.get("action_text"),
            start_date=self.cleaned_data.get("start_date"),
            completion_date=self.cleaned_data.get("completion_date"),
            action_type=self.cleaned_data.get("action_type"),
            action_type_category=action_type_category,
            stakeholders=self.cleaned_data["stakeholders"],
        )


class ActionPlanTaskEditOutcomeForm(
    ClearableMixin, SubformMixin, APIFormMixin, forms.Form
):

    outcome = forms.CharField(
        label="Outcome",
        widget=forms.Textarea(attrs={"class": "govuk-textarea"}),
        required=False,
    )

    def __init__(
        self, barrier_id, action_plan_id, milestone_id, task_id, *args, **kwargs
    ):
        self.barrier_id = barrier_id
        self.action_plan_id = action_plan_id
        self.milestone_id = milestone_id
        self.task_id = task_id
        super().__init__(*args, **kwargs)

    def save(self):
        client = MarketAccessAPIClient(self.token)

        client.action_plans.edit_task(
            barrier_id=self.barrier_id,
            task_id=self.task_id,
            outcome=self.cleaned_data["outcome"],
        )


class ActionPlanTaskEditProgressForm(
    ClearableMixin, SubformMixin, APIFormMixin, forms.Form
):

    progress = forms.CharField(
        label="Progress",
        widget=forms.Textarea(attrs={"class": "govuk-textarea"}),
        required=False,
    )

    def __init__(
        self, barrier_id, action_plan_id, milestone_id, task_id, *args, **kwargs
    ):
        self.barrier_id = barrier_id
        self.action_plan_id = action_plan_id
        self.milestone_id = milestone_id
        self.task_id = task_id
        super().__init__(*args, **kwargs)

    def save(self):
        client = MarketAccessAPIClient(self.token)

        client.action_plans.edit_task(
            barrier_id=self.barrier_id,
            task_id=self.task_id,
            progress=self.cleaned_data["progress"],
        )
