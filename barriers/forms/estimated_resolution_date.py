from django.forms import CharField, Form, Textarea

from barriers.forms.mixins import APIFormMixin
from utils.api.client import MarketAccessAPIClient
from utils.forms import EstimatedResolutionDateField


class AddEstimatedResolutionDateForm(APIFormMixin, Form):
    estimated_resolution_date = EstimatedResolutionDateField(
        label="Estimated resolution date",
        help_text="The date should be no more than 5 years in the future. Enter the date in the format, 11 2024.",
        error_messages={"required": "Enter an estimated resolution date"},
    )
    reason = CharField(
        label="How have you estimated this date?",
        widget=Textarea,
        max_length=1250
    )

    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.erd_request.create(
            barrier_id=str(self.id),
            estimated_resolution_date=str(
                self.cleaned_data.get("estimated_resolution_date")
            ),
            reason=self.cleaned_data.get("reason"),
        )


class EditEstimatedResolutionDateForm(APIFormMixin, Form):
    estimated_resolution_date = EstimatedResolutionDateField(
        label="Estimated resolution date",
        help_text="The date should be no more than 5 years in the future. Enter the date in the format, 11 2024.",
        error_messages={"required": "Enter an estimated resolution date"},
    )
    reason = CharField(
        label="How have you estimated this date?",
        widget=Textarea,
        max_length=1250
    )

    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.erd_request.create(
            barrier_id=str(self.id),
            estimated_resolution_date=str(
                self.cleaned_data.get("estimated_resolution_date")
            ),
            reason=self.cleaned_data.get("reason"),
        )


class DeleteEstimatedResolutionDateForm(APIFormMixin, Form):
    reason = CharField(
        label="Why do you want to remove the estimated resolution date?",
        widget=Textarea,
        max_length=1250
    )

    def save(self):
        client = MarketAccessAPIClient(self.token)
        reason = self.cleaned_data.get("reason")
        client.erd_request.delete(barrier_id=str(self.id), reason=reason)


class ReviewEstimatedResolutionDateForm(APIFormMixin, Form):
    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.erd_request.approve(barrier_id=str(self.id))


class ApproveEstimatedResolutionDateForm(APIFormMixin, Form):
    pass


class RejectEstimatedResolutionDateForm(APIFormMixin, Form):
    reason = CharField(
        label="Why do you want to reject the request to delete the estimated resolution date?",
        widget=Textarea,
        max_length=1250
    )

    def save(self):
        client = MarketAccessAPIClient(self.token)
        reason = self.cleaned_data.get("reason")
        client.erd_request.reject(barrier_id=str(self.id), reason=reason)


class ConfirmationEstimatedResolutionDateForm(APIFormMixin, Form):
    pass
