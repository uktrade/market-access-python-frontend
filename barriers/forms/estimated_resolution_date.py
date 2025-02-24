from django.forms import Form, CharField, Textarea

from utils.api.client import MarketAccessAPIClient
from utils.forms import EstimatedResolutionDateField


class AddEstimatedResolutionDateForm(Form):
    estimated_resolution_date = EstimatedResolutionDateField(
        label="Estimated resolution date",
        help_text="The date should be no more than 5 years in the future. Enter the date in the format, 11 2024.",
        error_messages={"required": "Enter an estimated resolution date"},
    )
    reason = CharField(
        label="What is the reason for adding the estimated resolution date?",
        widget=Textarea,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        self.token = kwargs.pop("token")
        self.barrier_id = kwargs.pop("barrier_id")
        kwargs.pop("id")
        return super().__init__(*args, **kwargs)

    def save(self):
        client = MarketAccessAPIClient(self.token)
        date = self.cleaned_data.get("estimated_resolution_date")
        client.erd_request.create(
            barrier_id=str(self.barrier_id),
            estimated_resolution_date=str(self.cleaned_data.get("estimated_resolution_date")),
            reason=self.cleaned_data.get("reason")
        )


class EditEstimatedResolutionDateForm(Form):
    estimated_resolution_date = EstimatedResolutionDateField(
        label="Estimated resolution date",
        help_text="The date should be no more than 5 years in the future. Enter the date in the format, 11 2024.",
        error_messages={"required": "Enter an estimated resolution date"},
    )
    reason = CharField(
        label="What is the reason for changing the estimated resolution date?",
        widget=Textarea,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        self.token = kwargs.pop("token")
        self.barrier_id = kwargs.pop("barrier_id")
        kwargs.pop("id")
        return super().__init__(*args, **kwargs)

    def save(self):
        client = MarketAccessAPIClient(self.token)
        date = self.cleaned_data.get("estimated_resolution_date")
        print('DATE: ', date)
        client.erd_request.create(
            barrier_id=str(self.barrier_id),
            estimated_resolution_date=str(self.cleaned_data.get("estimated_resolution_date")),
            reason=self.cleaned_data.get("reason")
        )


class DeleteEstimatedResolutionDateForm(Form):
    reason = CharField(
        label="Why do you want to remove the estimated resolution date?",
        widget=Textarea,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        self.token = kwargs.pop("token")
        self.barrier_id = kwargs.pop("barrier_id")
        kwargs.pop("id")
        return super().__init__(*args, **kwargs)

    def save(self):
        client = MarketAccessAPIClient(self.token)
        print("CLEANED_DATA: ", self.cleaned_data)
        reason = self.cleaned_data.get("reason")
        client.erd_request.delete(barrier_id=str(self.barrier_id), reason=reason)


class ReviewEstimatedResolutionDateForm(Form):
    reason = CharField(
        label="Why do you want to remove the estimated resolution date?",
        widget=Textarea,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        self.token = kwargs.pop("token")
        self.barrier_id = kwargs.pop("barrier_id")
        kwargs.pop("id")
        return super().__init__(*args, **kwargs)

    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.erd_request.approve(barrier_id=str(self.barrier_id))


class ApproveEstimatedResolutionDateForm(Form):
    def __init__(self, *args, **kwargs):
        self.token = kwargs.pop("token")
        self.barrier_id = kwargs.pop("barrier_id")
        kwargs.pop("id")
        return super().__init__(*args, **kwargs)


class RejectEstimatedResolutionDateForm(Form):
    reason = CharField(
        label="Why do you want to reject the request to delete the estimated resolution date?",
        widget=Textarea,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        self.token = kwargs.pop("token")
        self.barrier_id = kwargs.pop("barrier_id")
        kwargs.pop("id")
        return super().__init__(*args, **kwargs)

    def save(self):
        client = MarketAccessAPIClient(self.token)
        print("CLEANED_DATA: ", self.cleaned_data)
        reason = self.cleaned_data.get("reason")
        client.erd_request.reject(barrier_id=str(self.barrier_id), reason=reason)


class ConfirmationEstimatedResolutionDateForm(Form):
    def __init__(self, *args, **kwargs):
        self.token = kwargs.pop("token")
        self.barrier_id = kwargs.pop("barrier_id")
        kwargs.pop("id")
        return super().__init__(*args, **kwargs)
