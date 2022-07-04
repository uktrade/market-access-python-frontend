import logging

from django import forms
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone

from barriers.constants import (
    ACTION_PLAN_RAG_STATUS_CHOICES,
    ACTION_PLAN_TASK_CATEGORIES,
    ACTION_PLAN_TASK_CHOICES,
    ACTION_PLAN_TASK_TYPE_CHOICES,
)
from barriers.forms.mixins import APIFormMixin
from utils.api.client import MarketAccessAPIClient
from utils.forms import (
    ClearableMixin,
    MonthYearInFutureField,
    MultipleChoiceFieldWithHelpText,
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
        super().__init__(*args, **kwargs)

    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.action_plans.add_milestone(
            barrier_id=self.barrier_id,
            objective=self.cleaned_data.get("objective"),
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

    stakeholders = MultipleChoiceFieldWithHelpText(
        required=True,
        choices=[],
        widget=forms.CheckboxSelectMultiple,
        label="Stakeholders",
    )

    def __init__(self, barrier_id, action_plan_id, milestone_id, *args, **kwargs):
        self.barrier_id = barrier_id
        self.action_plan_id = action_plan_id
        self.milestone_id = milestone_id
        super().__init__(*args, **kwargs)

        # Get a list of stakeholders for the action plan - use action_plan_id
        # Set them as choices

        # TEMP STAKEHOLDER CLASS TO TEST STAKEHOLDER FUNCTIONS WHILE IT'S DEVED IN ANOTHER TICKET
        class Stakeholder:
            name = ""
            status = ""
            organisation = ""
            job_title = ""
            is_organisation = ""

            # The class "constructor" - It's actually an initializer
            def __init__(self, name, status, organisation, job_title, is_organisation):
                self.name = name
                self.status = status
                self.organisation = organisation
                self.job_title = job_title
                self.is_organisation = is_organisation

        stakeholder_1 = Stakeholder("Jim", "Friend", "HMRC", "Barista", False)
        stakeholder_2 = Stakeholder("Bob", "Target", "A Big Company", "Cleaner", False)
        stakeholder_3 = Stakeholder("Viv", "Friend", "DIT", "Security Guard", False)
        stakeholder_4 = Stakeholder("The UK Government", "Neutral", None, None, True)
        stakeholder_5 = Stakeholder("A Big Company", "Blocker", None, None, True)
        list_of_stakeholders = [
            stakeholder_1,
            stakeholder_2,
            stakeholder_3,
            stakeholder_4,
            stakeholder_5,
        ]

        # client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        # list_of_stakeholders = client.users.get(action_plan=action_plan_id)

        self.fields["stakeholders"].choices = list_of_stakeholders

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
        label="Intervention and purpose",
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
            ACTION_PLAN_TASK_TYPE_CHOICES.OTHER: action_plan_action_type_category_form_class_factory(  # noqa
                "OTHER"
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
        print("---------------")
        print(f"THE ASSIGNED TO INPUT: {email}")
        print(f"{query}")
        # UNCOMMENT THIS BEFORE PUSHING/MERGING
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
            action_type_category = "Other"

        print("****************")
        submitter = self.cleaned_data["assigned_to"]
        print(f"SUBMITTING THIS ASSIGNEES: {submitter}")
        print("****************")

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
