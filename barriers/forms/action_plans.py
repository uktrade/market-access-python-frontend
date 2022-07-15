import logging

from django import forms
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone

from barriers.constants import (
    ACTION_PLAN_RAG_STATUS_CHOICES,
    ACTION_PLAN_STAKEHOLDER_STATUS_CHOICES,
    ACTION_PLAN_STAKEHOLDER_TYPE_CHOICES,
    ACTION_PLAN_TASK_CATEGORIES,
    ACTION_PLAN_TASK_CHOICES,
    ACTION_PLAN_TASK_TYPE_CHOICES,
)
from barriers.forms.mixins import APIFormMixin
from utils.api.client import MarketAccessAPIClient
from utils.forms import (
    ClearableMixin,
    MonthYearInFutureField,
    SubformChoiceField,
    SubformMixin,
)
from utils.sso import SSOClient

logger = logging.getLogger(__name__)


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
        widget=forms.Textarea(attrs={"class": "govuk-textarea"}),
        label="Describe the objective",
        error_messages={"required": "Enter your milestone objective"},
        help_text="Describe the objective. "
        "For example ‘Scope the extent of this barrier via engagement with businesses’.",
    )

    def __init__(self, barrier_id, *args, **kwargs):
        self.barrier_id = barrier_id
        self.milestone_id = kwargs.pop("milestone_id", None)
        self.action_plan = kwargs.pop("action_plan")
        super().__init__(*args, **kwargs)

    def save(self):
        client = MarketAccessAPIClient(self.token)
        if self.milestone_id:
            client.action_plan_milestones.update_milestone(
                barrier_id=self.barrier_id,
                milestone_id=self.milestone_id,
                objective=self.cleaned_data.get("objective"),
            )
        else:
            client.action_plan_milestones.create_milestone(
                barrier_id=self.barrier_id,
                objective=self.cleaned_data.get("objective"),
            )

    def get_success_url(self):
        return reverse("barriers:action_plan", kwargs={"barrier_id": self.barrier_id})


def action_plan_action_type_category_form_class_factory(action_type: str):
    field_name = f"action_type_category_{action_type}"

    class ActionPlanActionTypeCategoryForm(forms.Form):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            if action_type != "OTHER":
                self.fields[field_name] = forms.ChoiceField(
                    label="Select category",
                    choices=ACTION_PLAN_TASK_CATEGORIES[action_type],
                )
            else:
                self.fields[field_name] = forms.CharField(
                    widget=forms.TextInput(attrs={"class": "govuk-input"}),
                    max_length=100,
                    label="Describe the task type",
                    error_messages={"required": "Enter your task type description"},
                )

        @property
        def get_field(self):
            return self[field_name]

        def get_action_type_category(self):
            return self.cleaned_data[field_name]

        def as_html(self):
            if action_type != "OTHER":
                template_name = "barriers/action_plans/action_type_category.html"
            else:
                template_name = "barriers/action_plans/action_type_category_other.html"
            return render_to_string(template_name, context={"form": self})

    return ActionPlanActionTypeCategoryForm


class ActionPlanTaskForm(ClearableMixin, SubformMixin, APIFormMixin, forms.Form):

    status = forms.ChoiceField(
        choices=ACTION_PLAN_TASK_CHOICES, widget=forms.RadioSelect
    )

    start_date = MonthYearInFutureField()
    completion_date = MonthYearInFutureField()

    action_text = forms.CharField(
        label="Provide a summary of the task and what it will involve",
        widget=forms.Textarea(attrs={"class": "govuk-textarea"}),
    )

    action_type = SubformChoiceField(
        label="Task type",
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
            ACTION_PLAN_TASK_TYPE_CHOICES.OTHER: action_plan_action_type_category_form_class_factory(  # noqa
                "OTHER"
            ),
        },
        widget=forms.RadioSelect,
    )

    # NEED TO DO THE NEW STAKEHOLDERS INPUT

    # NEED TO ASK ABOUT "ASSIGNED TO" DESIGN - ARE WE INTENDING FOR MORE THAN ONE ASSIGNED PERSON?
    # THERE SEEMS TO BE A NAME IN A BOX ABOVE THE TEXT INPUT WHICH CAN BE DELETED, LIKE A LIST ITEM.

    assigned_to = forms.CharField(
        widget=forms.TextInput(attrs={"class": "govuk-input"})
    )

    assigned_stakeholders = forms.MultipleChoiceField(
        required=True,
        choices=[],
        widget=forms.CheckboxSelectMultiple(attrs={"class": "govuk-checkboxes__input"}),
        label="Stakeholders",
        help_text="Add relevant stakeholders to the task",
    )

    def __init__(self, barrier_id, *args, **kwargs):
        self.barrier_id = barrier_id
        self.action_plan = kwargs.pop("action_plan")
        self.milestone_id = kwargs.pop("milestone_id")
        self.task_id = kwargs.pop("task_id")
        super().__init__(*args, **kwargs)

        stakeholders = self.action_plan.stakeholders
        self.fields["assigned_stakeholders"].choices = [
            (stakeholder.id, stakeholder) for stakeholder in stakeholders
        ]

    def clean_start_date(self):
        return self.cleaned_data["start_date"].isoformat()

    def clean_completion_date(self):
        return self.cleaned_data["completion_date"].isoformat()

    def clean_assigned_to(self):

        # THIS FUNCTION NOW NEEDS TO ACCEPT MULTIPLE USERS

        sso_client = SSOClient()
        email = self.cleaned_data["assigned_to"]
        query = email.replace(".", " ").split("@")[0]
        results = sso_client.search_users(query)
        print("---------------")
        print(f"{query}")
        # UNCOMMENT THIS BEFORE PUSHING/MERGING
        # USING PLACEHOLDER TO GET AROUND SSO VERIFICATION LOCALLY
        # if not results:
        #    raise ValidationError(f"Invalid user {query}")
        # for result in results:
        #    if result["email"] == email:
        #        return result["user_id"]
        # return
        return "9affb723-21d8-43c5-82ac-f525bf02444f"

    def save(self):
        client = MarketAccessAPIClient(self.token)

        action_type_field = self.fields["action_type"]
        if hasattr(action_type_field, "subform"):
            action_type_category = action_type_field.subform.get_action_type_category()
        else:
            action_type_category = ""

        save_kwargs = {
            "barrier_id": self.barrier_id,
            "assigned_to": self.cleaned_data["assigned_to"],
            "status": self.cleaned_data.get("status"),
            "action_text": self.cleaned_data.get("action_text"),
            "start_date": self.cleaned_data.get("start_date"),
            "completion_date": self.cleaned_data.get("completion_date"),
            "action_type": self.cleaned_data.get("action_type"),
            "action_type_category": action_type_category,
            "assigned_stakeholders": self.cleaned_data["assigned_stakeholders"],
        }
        if self.task_id:
            save_kwargs["task_id"] = self.task_id
            client.action_plan_tasks.update_task(**save_kwargs)
        else:
            client.action_plan_tasks.create_task(**save_kwargs)


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

        client.action_plans.update_task(
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

        client.action_plans.update_task(
            barrier_id=self.barrier_id,
            task_id=self.task_id,
            progress=self.cleaned_data["progress"],
        )


class ActionPlanStakeholderFormMixin:
    def __init__(self, barrier_id, *args, **kwargs):
        self.barrier_id = barrier_id
        self.stakeholder_id = kwargs.pop("stakeholder_id", None)
        self.action_plan = kwargs.pop("action_plan")
        super().__init__(*args, **kwargs)

    def get_request_data(self):
        return {}

    def save(self):
        client = MarketAccessAPIClient(self.token)

        request_data = self.get_request_data()
        if self.stakeholder_id:
            stakeholder = client.action_plan_stakeholders.update_stakeholder(
                barrier_id=self.barrier_id, id=self.stakeholder_id, **request_data
            )
        else:
            stakeholder = client.action_plan_stakeholders.create_stakeholder(
                barrier_id=self.barrier_id, **request_data
            )
        return stakeholder


class ActionPlanStakeholderTypeForm(
    ActionPlanStakeholderFormMixin,
    ClearableMixin,
    APIFormMixin,
    forms.Form,
):
    is_organisation = forms.ChoiceField(
        choices=ACTION_PLAN_STAKEHOLDER_TYPE_CHOICES.choices,
        widget=forms.RadioSelect(attrs={"class": "govuk-radios__input"}),
        label="Stakeholder type",
        required=True,
    )

    def get_request_data(self):
        request_data = super().get_request_data()
        request_data["is_organisation"] = (
            self.cleaned_data["is_organisation"]
            == ACTION_PLAN_STAKEHOLDER_TYPE_CHOICES.ORGANISATION
        )
        return request_data


class ActionPlanOrganisationStakeholderDetailsForm(
    ActionPlanStakeholderFormMixin,
    ClearableMixin,
    APIFormMixin,
    forms.Form,
):
    name = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={"class": "govuk-input"}),
    )
    status = forms.ChoiceField(
        choices=ACTION_PLAN_STAKEHOLDER_STATUS_CHOICES.choices,
        widget=forms.RadioSelect(attrs={"class": "govuk-radios__input"}),
        label="Status",
        required=True,
    )

    def get_request_data(self):
        request_data = super().get_request_data()
        request_data["name"] = self.cleaned_data["name"]
        request_data["status"] = self.cleaned_data["status"]
        return request_data


class ActionPlanIndividualStakeholderDetailsForm(
    ActionPlanOrganisationStakeholderDetailsForm
):
    organisation = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={"class": "govuk-input"}),
    )
    job_title = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={"class": "govuk-input"}),
    )

    def get_request_data(self):
        request_data = super().get_request_data()
        request_data["organisation"] = self.cleaned_data["organisation"]
        request_data["job_title"] = self.cleaned_data["job_title"]
        return request_data
