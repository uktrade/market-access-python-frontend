import logging
import uuid

import requests
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from utils.api.client import MarketAccessAPIClient
from utils.exceptions import FileUploadError, ScanError
from utils.forms.fields import MonthYearInFutureField

logger = logging.getLogger(__name__)


class APIFormMixin:
    def __init__(self, *args, **kwargs):
        id = kwargs.pop("id", None)
        if isinstance(id, uuid.UUID):
            id = str(id)
        self.id = id
        self.token = kwargs.pop("token", None)

        # todo - Explore moving this higher up the chain as not needed for all api forms
        self.item_id = kwargs.pop("item_id", None)
        self.barrier_id = kwargs.pop("barrier_id", None)
        self.progress_update_id = kwargs.pop("progress_update_id", None)
        self.action_plan = kwargs.pop("action_plan", None)
        self.milestone_id = kwargs.pop("milestone_id", None)
        self.task_id = kwargs.pop("task_id", None)
        super().__init__(*args, **kwargs)


class DocumentMixin:
    """
    Helper functions to upload the 'document' field of a form.

    1. Calls the API with file name and size, getting back a document id
       and signed url for uploading to S3.
    2. Uploads the file to S3.
    3. Calls the API confirming that the file has been uploaded.
    4. Polls the API until the virus scan is complete, raising an exception
       if it fails the check.
    """

    def __init__(self, *args, **kwargs):
        self.token = kwargs.pop("token")
        super().__init__(*args, **kwargs)

    def validate_document(self, field_name="document"):
        """
        Only uploads files when javascript is disabled
        """
        document = self.cleaned_data.get(field_name)
        document_id_field_name = self.get_document_id_field_name(field_name)
        multi_value = hasattr(self.fields.get(document_id_field_name), "choices")

        if document:
            try:
                uploaded_document = self.upload_document(field_name)
                if multi_value:
                    document_ids = self.cleaned_data.get(document_id_field_name, [])
                    document_ids.append(uploaded_document["id"])
                    self.cleaned_data[document_id_field_name] = document_ids
                else:
                    self.cleaned_data[document_id_field_name] = uploaded_document["id"]
            except FileUploadError as e:
                self.add_error(field_name, str(e))
            except ScanError as e:
                self.add_error(field_name, str(e))
        return document

    def get_document_id_field_name(self, field_name):
        if f"{field_name}_id" in self.fields:
            return f"{field_name}_id"
        elif f"{field_name}_ids" in self.fields:
            return f"{field_name}_ids"

    def upload_document(self, field_name="document"):
        # to avoid circular imports
        from utils.api.client import MarketAccessAPIClient

        document = self.cleaned_data[field_name]

        client = MarketAccessAPIClient(self.token)
        data = client.documents.create(
            filename=document.name,
            filesize=document.size,
        )
        document_id = data["id"]

        self.upload_to_s3(url=data["signed_upload_url"], document=document)

        client.documents.complete_upload(document_id)
        client.documents.check_scan_status(document_id)

        return {
            "id": document_id,
            "file": {
                "name": document.name,
                "size": document.size,
            },
        }

    def upload_to_s3(self, url, document):
        document.seek(0)
        response = requests.put(
            url,
            headers={
                "x-amz-server-side-encryption": "AES256",
            },
            data=document,
        )
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            raise FileUploadError(
                "A system error has occured, so the file has not been "
                "uploaded. Try again."
            )

    def is_multi_document(self):
        """
        Is the submitted field a multi document field
        """
        for field_name, field in self.fields.items():
            if self.cleaned_data.get(field_name):
                return field.multi_document


class EstimatedResolutionDateApprovalMixin(APIFormMixin):
    estimated_resolution_date = MonthYearInFutureField(
        label="Estimated resolution date",
        help_text="For example, 11 2024",
        error_messages={"required": "Enter an estimated resolution date"},
    )
    estimated_resolution_date_change_reason = forms.CharField(
        label="What has caused the change in estimated resolution date?",
        widget=forms.Textarea,
        required=False,
    )

    @property
    def barrier(self):
        client = MarketAccessAPIClient(self.token)
        return client.barriers.get(id=self.barrier_id)

    @property
    def is_user_admin(self):
        return self.user.has_permission("can_approve_estimated_completion_date")

    def does_new_estimated_date_require_approval(self, cleaned_data):
        estimated_resolution_date = cleaned_data.get("estimated_resolution_date")
        if not self.barrier.estimated_resolution_date:
            return False

        if not estimated_resolution_date:
            return False

        existing_estimated_resolution_date = (
            self.barrier.estimated_resolution_date.strftime("%Y-%m-%d")
        )

        return existing_estimated_resolution_date and (
            estimated_resolution_date > existing_estimated_resolution_date
        )

    def does_change_require_approval(self, cleaned_data):
        return (not self.is_user_admin) and (
            not self.does_new_estimated_date_require_approval(cleaned_data)
        )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")

        super().__init__(*args, **kwargs)

        self.barrier_id = kwargs.pop("barrier_id")
        if "progress_update_id" in kwargs:
            self.progress_update_id = kwargs.pop("progress_update_id")
        self.estimated_resolution_date = kwargs.get("initial", {}).get(
            "estimated_resolution_date"
        )

    def clean_estimated_resolution_date(self):
        return self.cleaned_data["estimated_resolution_date"].isoformat()

    def clean(self, *args, **kwargs):
        cleaned_data = super().clean(*args, **kwargs)
        change_requires_approval = self.does_new_estimated_date_require_approval(
            cleaned_data
        )

        if (not self.is_user_admin) and change_requires_approval:
            # only admin users can change the estimated resolution date to a date in the past
            # without approval
            if not cleaned_data.get("estimated_resolution_date_change_reason"):
                self.add_error(
                    "estimated_resolution_date_change_reason",
                    ValidationError(
                        _("Enter what has caused the change in date"),
                        code="missing_update",
                    ),
                )

        return cleaned_data

    def save(self):
        client = MarketAccessAPIClient(self.token)

        estimated_resolution_date = self.cleaned_data.get("estimated_resolution_date")
        is_future_date = self.does_new_estimated_date_require_approval(
            self.cleaned_data
        )

        if (not self.is_user_admin) and (is_future_date):
            self.requested_change = True
            client.barriers.patch(
                id=str(self.barrier_id),
                proposed_estimated_resolution_date=estimated_resolution_date,
                estimated_resolution_date_change_reason=self.cleaned_data.get(
                    "estimated_resolution_date_change_reason"
                ),
            )
        else:
            self.requested_change = False
            client.barriers.patch(
                id=str(self.barrier_id),
                estimated_resolution_date=estimated_resolution_date,
                proposed_estimated_resolution_date=estimated_resolution_date,
                estimated_resolution_date_change_reason=self.cleaned_data.get(
                    "estimated_resolution_date_change_reason", ""
                ),
            )
