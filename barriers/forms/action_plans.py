import logging

from django import forms
from django.forms import ValidationError
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe

from barriers.constants import (
    ACTION_PLAN_HAS_RISKS_CHOICES,
    ACTION_PLAN_RAG_STATUS_CHOICES,
    ACTION_PLAN_RISK_LEVEL_CHOICES,
    ACTION_PLAN_STAKEHOLDER_STATUS_CHOICES,
    ACTION_PLAN_STAKEHOLDER_TYPE_CHOICES,
    ACTION_PLAN_TASK_CATEGORIES,
    ACTION_PLAN_TASK_CHOICES,
    ACTION_PLAN_TASK_TYPE_CHOICES,
)
from barriers.forms.mixins import APIFormMixin
from utils.api.client import MarketAccessAPIClient
from utils.forms.fields import MonthYearInFutureField, SubformChoiceField
from utils.forms.mixins import ClearableMixin, SubformMixin
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
        label="Action plan overview",
        help_text="Give a short summary of how you plan to resolve this barrier."
        " You can add specific tasks and actions to the objective section of your action plan.",
        required=True,
    )

    def __init__(self, barrier_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.barrier_id = barrier_id
        self.action_plan = kwargs.pop("action_plan", None)

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
        label="Add an objective",
        error_messages={"required": "Enter an objective"},
        help_text=(
            "Name your objective. For example, ‘Engage with companies to scope extent"
            " of barrier."
        ),
    )

    def __init__(self, barrier_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.barrier_id = barrier_id
        self.milestone_id = kwargs.pop("milestone_id", None)
        self.action_plan = kwargs.pop("action_plan")

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
            id = kwargs.pop("id", None)
            token = kwargs.pop("token", None)
            milestone_id = kwargs.pop("milestone_id", None)
            action_plan = kwargs.pop("action_plan", None)
            task_id = kwargs.pop("task_id", None)
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
                    error_messages={"required": "Enter a description"},
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


class ActionPlanTaskFormMixin:
    def __init__(self, barrier_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.barrier_id = barrier_id
        self.action_plan = kwargs.pop("action_plan", None)
        self.milestone_id = kwargs.pop("milestone_id", None)
        self.task_id = kwargs.pop("task_id", None)

        stakeholders = self.action_plan.stakeholders
        self.fields["assigned_stakeholders"].choices = [
            (stakeholder.id, stakeholder) for stakeholder in stakeholders
        ]

    def save(self):
        client = MarketAccessAPIClient(self.token)

        save_kwargs = self.get_save_kwargs()
        if self.task_id:
            save_kwargs["task_id"] = self.task_id
            client.action_plan_tasks.update_task(**save_kwargs)
        else:
            client.action_plan_tasks.create_task(**save_kwargs)

    def get_save_kwargs(self):
        status = self.cleaned_data.get("status")
        save_kwargs = {
            "barrier_id": self.barrier_id,
            "milestone_id": self.milestone_id,
            "assigned_to": self.cleaned_data["assigned_to"],
            "status": status,
            "action_text": self.cleaned_data.get("action_text"),
            "start_date": self.cleaned_data.get("start_date"),
            "completion_date": self.cleaned_data.get("completion_date"),
            "action_type": self.cleaned_data.get("action_type"),
            "action_type_category": self.cleaned_data.get("action_type_category"),
            "assigned_stakeholders": self.cleaned_data["assigned_stakeholders"],
        }
        if (
            hasattr(self.fields["status"], "subforms")
            and status in self.fields["status"].subforms
        ):
            for status_name, status_text in (
                self.fields["status"].subforms[status].cleaned_data.items()
            ):
                save_kwargs[status_name] = status_text
        return save_kwargs


class ActionPlanTaskSubformRenderer:
    def as_html(self):
        if hasattr(self, "template_name"):
            template_name = self.template_name
        else:
            template_name = "django/forms/widgets/textarea.html"
        output = ""
        for field_name, field in self.fields.items():
            field.widget.name = field_name
            if field_name in self.initial:
                field.widget.value = self.initial[field_name]
            output += render_to_string(template_name, context={"widget": field.widget})
        return mark_safe(output)


class ActionPlanTaskEditOutcomeForm(
    ActionPlanTaskSubformRenderer,
    ClearableMixin,
    APIFormMixin,
    forms.Form,
):

    outcome = forms.CharField(
        label="Provide outcome of objective task",
        widget=forms.Textarea(attrs={"class": "govuk-textarea", "id": "id_outcome"}),
        required=False,
    )

    @property
    def label(self):
        return self.fields["outcome"].label

    @property
    def id_for_label(self):
        return self.fields["outcome"].widget.attrs["id"]

    def save(self):
        client = MarketAccessAPIClient(self.token)

        client.action_plans.update_task(
            barrier_id=self.barrier_id,
            task_id=self.task_id,
            outcome=self.cleaned_data["outcome"],
        )


class ActionPlanTaskEditProgressForm(
    ActionPlanTaskSubformRenderer,
    ClearableMixin,
    APIFormMixin,
    forms.Form,
):
    progress = forms.CharField(
        label="Provide progress of objective task",
        widget=forms.Textarea(attrs={"class": "govuk-textarea", "id": "id_progress"}),
        required=False,
    )

    @property
    def label(self):
        return self.fields["progress"].label

    @property
    def id_for_label(self):
        return self.fields["progress"].widget.attrs["id"]

    def save(self):
        client = MarketAccessAPIClient(self.token)

        client.action_plans.update_task(
            barrier_id=self.barrier_id,
            task_id=self.task_id,
            progress=self.cleaned_data["progress"],
        )


class ActionPlanTaskForm(
    ActionPlanTaskFormMixin, ClearableMixin, SubformMixin, APIFormMixin, forms.Form
):

    status = SubformChoiceField(
        choices=ACTION_PLAN_TASK_CHOICES,
        widget=forms.RadioSelect,
        subform_classes={
            ACTION_PLAN_TASK_CHOICES.IN_PROGRESS: ActionPlanTaskEditProgressForm,
            ACTION_PLAN_TASK_CHOICES.COMPLETED: ActionPlanTaskEditOutcomeForm,
        },
    )

    start_date = MonthYearInFutureField()
    completion_date = MonthYearInFutureField(
        label="Estimated completion date",
        help_text=(
            "When do you expect to finish this task? You can change this date if the"
            " situation changes."
        ),
    )

    action_text = forms.CharField(
        label="Provide a summary of the task and what it will involve",
        widget=forms.Textarea(attrs={"class": "govuk-textarea"}),
        error_messages={
            "required": "Enter a summary",
        },
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

    assigned_to = forms.CharField(
        widget=forms.TextInput(attrs={"class": "govuk-input govuk-input--width-20"}),
        error_messages={
            "required": "Assign this task to someone",
        },
        help_text="Enter an email address and press return to assign this task to someone.",
    )

    assigned_stakeholders = forms.MultipleChoiceField(
        required=False,
        choices=[],
        widget=forms.CheckboxSelectMultiple(attrs={"class": "govuk-checkboxes__input"}),
        label="Stakeholders",
        help_text="Select relevant stakeholders to add their name to this task. "
        "This information is only viewable within the action plan.",
    )

    def clean_start_date(self):
        return self.cleaned_data["start_date"].isoformat()

    def clean_completion_date(self):
        return self.cleaned_data["completion_date"].isoformat()

    def clean_assigned_to(self):
        sso_client = SSOClient()
        email = self.cleaned_data["assigned_to"]
        result = sso_client.get_user_by_email(email)
        if result is None:
            raise ValidationError(f"Invalid user {email}")
        return result["user_id"]

    def clean_action_type(self):
        action_type = self.data["action_type"]
        subform = self.fields["action_type"].subforms[action_type]
        subform.full_clean()
        action_type_category_name = f"action_type_category_{action_type}"
        action_type_category = self.data[action_type_category_name]
        self.cleaned_data["action_type_category"] = action_type_category
        return action_type


class ActionPlanTaskDateChangeReasonForm(
    ActionPlanTaskFormMixin, APIFormMixin, forms.Form
):
    reason_for_completion_date_change = forms.CharField(
        required=True,
        widget=forms.Textarea(
            attrs={
                "class": "govuk-textarea",
                "rows": 4,
            }
        ),
        error_messages={
            "required": "Enter a reason",
        },
        help_text="Provide the reason the estimated completion date has changed.",
    )

    status = forms.CharField(widget=forms.HiddenInput)
    start_date = forms.CharField(widget=forms.HiddenInput)
    completion_date = forms.CharField(widget=forms.HiddenInput)
    action_text = forms.CharField(widget=forms.HiddenInput)
    assigned_to = forms.CharField(widget=forms.HiddenInput)
    action_type = forms.CharField(widget=forms.HiddenInput)
    action_type_category = forms.CharField(widget=forms.HiddenInput)
    assigned_stakeholders = forms.MultipleChoiceField(
        required=False,
        choices=[],
        widget=forms.MultipleHiddenInput(),
    )
    progress = forms.CharField(widget=forms.HiddenInput, required=False)
    outcome = forms.CharField(widget=forms.HiddenInput, required=False)

    def get_save_kwargs(self):
        save_kwargs = super().get_save_kwargs()
        save_kwargs["reason_for_completion_date_change"] = self.cleaned_data[
            "reason_for_completion_date_change"
        ]
        return save_kwargs

    def __init__(self, barrier_id, *args, **kwargs):
        super().__init__(barrier_id, *args, **kwargs)


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

    def __init__(self, barrier_id, action_plan, *args, **kwargs):
        self.barrier_id = barrier_id
        self.action_plan = action_plan
        return super().__init__(*args, **kwargs)

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
        label="Organisation name",
        widget=forms.TextInput(attrs={"class": "govuk-input govuk-input--width-20"}),
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
        request_data["is_organisation"] = True
        return request_data


class ActionPlanIndividualStakeholderDetailsForm(
    ActionPlanOrganisationStakeholderDetailsForm
):
    name = forms.CharField(
        max_length=255,
        required=True,
        label="Name",
        widget=forms.TextInput(attrs={"class": "govuk-input govuk-input--width-20"}),
    )
    job_title = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={"class": "govuk-input govuk-input--width-20"}),
    )
    organisation = forms.CharField(
        max_length=255,
        required=True,
        label="Organisation name",
        widget=forms.TextInput(attrs={"class": "govuk-input govuk-input--width-20"}),
    )
    status = forms.ChoiceField(
        choices=ACTION_PLAN_STAKEHOLDER_STATUS_CHOICES.choices,
        widget=forms.RadioSelect(attrs={"class": "govuk-radios__input"}),
        label="Status",
        required=True,
    )

    def get_request_data(self):
        request_data = super().get_request_data()
        request_data["organisation"] = self.cleaned_data["organisation"]
        request_data["job_title"] = self.cleaned_data["job_title"]
        request_data["is_organisation"] = False
        return request_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.barrier_id = kwargs.pop("barrier_id", None)


class ActionPlanRisksAndMitigationForm(
    ClearableMixin, SubformMixin, APIFormMixin, forms.Form
):

    has_risks = forms.ChoiceField(
        label="Could trying to resolve this barrier lead to outcomes that are not good for the UK?",
        choices=ACTION_PLAN_HAS_RISKS_CHOICES,
        widget=forms.RadioSelect(attrs={"class": "govuk-radios__input"}),
    )

    potential_risks = forms.CharField(
        label="What are the risks?",
        widget=forms.Textarea(attrs={"class": "govuk-textarea"}),
        required=False,
        help_text="For example, could our efforts make the barrier worse or cause tensions with the affected country.",
    )

    risk_level = forms.ChoiceField(
        label="What is the risk level?",
        choices=ACTION_PLAN_RISK_LEVEL_CHOICES,
        required=False,
        widget=forms.RadioSelect(attrs={"class": "govuk-radios__input"}),
    )

    risk_mitigation_measures = forms.CharField(
        label="How will you mitigate the risks?",
        widget=forms.Textarea(attrs={"class": "govuk-textarea"}),
        required=False,
        help_text="Are there actions you can take to avoid a negative outcome?",
    )

    def __init__(self, barrier_id, action_plan, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.barrier_id = barrier_id
        # self.action_plan_id = action_plan_id

    def clean(self):
        cleaned_data = super().clean()
        has_risks = cleaned_data.get("has_risks")
        if has_risks == ACTION_PLAN_HAS_RISKS_CHOICES.YES:
            if not cleaned_data.get("potential_risks"):
                self.add_error("potential_risks", "Enter the risks")
            if not cleaned_data.get("risk_level"):
                self.add_error("risk_level", "Select a risk level")
            if not cleaned_data.get("risk_mitigation_measures"):
                self.add_error(
                    "risk_mitigation_measures",
                    "Enter actions to mitigate the risks",
                )
        return cleaned_data

    def save(self):
        client = MarketAccessAPIClient(self.token)

        has_risks = self.cleaned_data["has_risks"]

        cleaned_data = self.cleaned_data

        if has_risks == ACTION_PLAN_HAS_RISKS_CHOICES.YES:
            client.action_plans.edit_action_plan(
                barrier_id=self.barrier_id,
                has_risks=cleaned_data["has_risks"],
                potential_risks=cleaned_data["potential_risks"],
                risk_level=cleaned_data["risk_level"],
                risk_mitigation_measures=cleaned_data["risk_mitigation_measures"],
            )
        else:
            client.action_plans.edit_action_plan(
                barrier_id=self.barrier_id, has_risks=cleaned_data["has_risks"]
            )


class ActionPlanRisksAndMitigationIntroForm(
    ClearableMixin, SubformMixin, APIFormMixin, forms.Form
):
    has_risks = forms.ChoiceField(
        label="Could trying to resolve this barrier lead to outcomes that are not good for the UK?",
        choices=ACTION_PLAN_HAS_RISKS_CHOICES,
        widget=forms.RadioSelect(attrs={"class": "govuk-radios__input"}),
    )

    def __init__(self, barrier_id, action_plan, *args, **kwargs):
        self.barrier_id = barrier_id
        # self.action_plan_id = action_plan_id
        super().__init__(*args, **kwargs)

    def save(self):
        client = MarketAccessAPIClient(self.token)

        client.action_plans.edit_action_plan(
            barrier_id=self.barrier_id,
            has_risks=self.cleaned_data["has_risks"],
        )
