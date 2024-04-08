import logging
from http import HTTPStatus

from django.urls import reverse
from mock import patch

from core.tests import MarketAccessTestCase

logger = logging.getLogger(__name__)


class EditPublicBarrierTitleTestCase(MarketAccessTestCase):
    def test_edit_title_has_initial_data(self):
        response = self.client.get(
            reverse(
                "barriers:edit_public_barrier_title",
                kwargs={"barrier_id": self.barrier["id"], "countdown": 12},
            )
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert form.initial["title"] == self.public_barrier["title"]

    @patch("utils.api.resources.PublicBarriersResource.report_public_barrier_field")
    def test_title_cannot_be_empty(self, mock_patch):
        response = self.client.post(
            reverse(
                "barriers:edit_public_barrier_title",
                kwargs={"barrier_id": self.barrier["id"], "countdown": 15},
            ),
            data={"title": ""},
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert form.is_valid() is False
        assert "title" in form.errors
        assert mock_patch.called is False

    @patch("utils.api.resources.PublicBarriersResource.report_public_barrier_field")
    @patch("django.contrib.messages.add_message")
    def test_edit_title_calls_api(self, mock_add_message, mock_patch):
        mock_patch.return_value = self.barrier
        response = self.client.post(
            reverse(
                "barriers:edit_public_barrier_title",
                kwargs={"barrier_id": self.barrier["id"], "countdown": 5},
            ),
            data={"title": "New Title"},
        )
        mock_patch.assert_called_with(
            id=self.barrier["id"],
            form_name="barrier-public-title",
            values={"title": "New Title"},
        )
        assert response.status_code == HTTPStatus.FOUND

        expected_message_tag = "The public title has been added"
        assert mock_add_message.called is True
        assert expected_message_tag in str(mock_add_message.call_args)


class EditPublicBarrierSummaryTestCase(MarketAccessTestCase):
    def test_edit_summary_has_initial_data(self):
        response = self.client.get(
            reverse(
                "barriers:edit_public_barrier_summary",
                kwargs={"barrier_id": self.barrier["id"], "countdown": 17},
            )
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert form.initial["summary"] == self.public_barrier["summary"]

    @patch("utils.api.resources.PublicBarriersResource.report_public_barrier_field")
    def test_summary_cannot_be_empty(self, mock_patch):
        response = self.client.post(
            reverse(
                "barriers:edit_public_barrier_summary",
                kwargs={"barrier_id": self.barrier["id"], "countdown": 20},
            ),
            data={"summary": ""},
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert form.is_valid() is False
        assert "summary" in form.errors
        assert mock_patch.called is False

    @patch("utils.api.resources.PublicBarriersResource.report_public_barrier_field")
    @patch("django.contrib.messages.add_message")
    def test_edit_summary_calls_api(self, mock_add_message, mock_patch):
        mock_patch.return_value = self.barrier
        response = self.client.post(
            reverse(
                "barriers:edit_public_barrier_summary",
                kwargs={"barrier_id": self.barrier["id"], "countdown": 24},
            ),
            data={"summary": "New summary"},
        )
        mock_patch.assert_called_with(
            id=self.barrier["id"],
            form_name="barrier-public-summary",
            values={"summary": "New summary"},
        )
        assert response.status_code == HTTPStatus.FOUND

        expected_message_tag = "The public summary has been added"
        assert mock_add_message.called is True
        assert expected_message_tag in str(mock_add_message.call_args)


class EditPublicBarrierEligibilityTestCase(MarketAccessTestCase):
    def test_eligibility_has_initial_data(self):
        response = self.client.get(
            reverse(
                "barriers:edit_public_eligibility",
                kwargs={"barrier_id": self.barrier["id"], "countdown": 27},
            )
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert (
            form.initial["public_eligibility"] == "yes"
            if self.barrier["public_eligibility"]
            else "no"
        )
        assert (
            form.initial["allowed_summary"]
            == self.barrier["public_eligibility_summary"]
        )

    @patch("utils.api.resources.APIResource.patch")
    def test_eligibility_cannot_be_empty(self, mock_patch):
        response = self.client.post(
            reverse(
                "barriers:edit_public_eligibility",
                kwargs={"barrier_id": self.barrier["id"], "countdown": 20},
            ),
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert form.is_valid() is False
        assert "public_eligibility" in form.errors
        assert mock_patch.called is False

    @patch("utils.api.resources.APIResource.patch")
    @patch("django.contrib.messages.add_message")
    def test_edit_eligibility_yes_calls_api(self, mock_add_message, mock_patch):
        mock_patch.return_value = self.barrier
        response = self.client.post(
            reverse(
                "barriers:edit_public_eligibility",
                kwargs={"barrier_id": self.barrier["id"], "countdown": 30},
            ),
            data={"public_eligibility": "yes", "public_eligibility_summary": ""},
        )
        mock_patch.assert_called_with(
            id=self.barrier["id"],
            public_eligibility="yes",
            public_eligibility_summary="",
        )
        assert response.status_code == HTTPStatus.FOUND

        expected_message_tag = "The barrier publication status has been set to: allowed"
        assert mock_add_message.called is True
        assert expected_message_tag in str(mock_add_message.call_args)

    @patch("utils.api.resources.APIResource.patch")
    @patch("utils.api.resources.PublicBarriersResource.report_public_barrier_field")
    @patch("django.contrib.messages.add_message")
    def test_edit_eligibility_no_calls_api(
        self, mock_add_message, mock_report, mock_patch
    ):
        mock_patch.return_value = self.barrier
        response = self.client.post(
            reverse(
                "barriers:edit_public_eligibility",
                kwargs={"barrier_id": self.barrier["id"], "countdown": 3},
            ),
            data={"public_eligibility": "no", "public_eligibility_summary": "summary"},
        )
        mock_patch.assert_called_with(
            id=self.barrier["id"],
            public_eligibility="no",
            public_eligibility_summary="summary",
        )

        assert mock_report.call_count == 2
        mock_report.assert_any_call(
            id=self.barrier["id"],
            form_name="barrier-public-title",
            values={"title": ""},
        )
        mock_report.assert_any_call(
            id=self.barrier["id"],
            form_name="barrier-public-summary",
            values={"summary": ""},
        )
        assert response.status_code == HTTPStatus.FOUND

        expected_message_tag = "The publication status is set to: not allowed"
        assert mock_add_message.called is True
        assert expected_message_tag in str(mock_add_message.call_args)


class ApprovePublicBarrierSummaryTestCase(MarketAccessTestCase):
    @patch("utils.api.resources.PublicBarriersResource.ready_for_publishing")
    @patch("utils.api.resources.PublicBarriersResource.patch")
    @patch("django.contrib.messages.add_message")
    def test_approve_with_summary(self, mock_add_message, mock_patch, mock_ready):
        response = self.client.post(
            reverse(
                "barriers:approve_public_barrier_confirmation",
                kwargs={"barrier_id": self.barrier["id"], "countdown": 17},
            ),
            data={
                "content_clearance": True,
                "external_clearances": True,
                "public_approval_summary": "Test summary",
                "submit_approval": "Send to GOV.UK content team",
            },
        )
        assert response.status_code == HTTPStatus.FOUND
        assert mock_ready.called is True
        assert mock_patch.called is True
        assert mock_patch.call_count == 1

        expected_message_tag = (
            "This barrier has been approved and is now with the GOV.UK content team"
        )
        assert mock_add_message.called is True
        assert expected_message_tag in str(mock_add_message.call_args)

    @patch("utils.api.resources.PublicBarriersResource.ready_for_publishing")
    @patch("utils.api.resources.PublicBarriersResource.patch")
    @patch("django.contrib.messages.add_message")
    def test_approve_without_summary(self, mock_add_message, mock_patch, mock_ready):
        response = self.client.post(
            reverse(
                "barriers:approve_public_barrier_confirmation",
                kwargs={"barrier_id": self.barrier["id"], "countdown": 30},
            ),
            data={
                "content_clearance": True,
                "external_clearances": True,
                "public_approval_summary": "",
                "submit_approval": "Send to GOV.UK content team",
            },
        )
        assert response.status_code == HTTPStatus.FOUND
        assert mock_ready.called is True
        assert mock_patch.called is False

        expected_message_tag = (
            "This barrier has been approved and is now with the GOV.UK content team"
        )
        assert mock_add_message.called is True
        assert expected_message_tag in str(mock_add_message.call_args)

    @patch("utils.api.resources.PublicBarriersResource.ready_for_publishing")
    @patch("utils.api.resources.PublicBarriersResource.patch")
    def test_approve_failure(self, mock_patch, mock_ready):
        response = self.client.post(
            reverse(
                "barriers:approve_public_barrier_confirmation",
                kwargs={"barrier_id": self.barrier["id"], "countdown": 18},
            ),
            data={
                "content_clearance": False,
                "external_clearances": False,
                "public_approval_summary": "",
                "submit_approval": "Send to GOV.UK content team",
            },
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert form.is_valid() is False
        assert "content_clearance" in form.errors
        assert "external_clearances" in form.errors
        assert mock_ready.called is False
        assert mock_patch.called is False

    @patch("utils.api.resources.PublicBarriersResource.ready_for_publishing")
    @patch("utils.api.resources.PublicBarriersResource.patch")
    @patch("django.contrib.messages.add_message")
    @patch("utils.api.resources.BarriersResource.patch")
    @patch("utils.api.resources.PublicBarriersResource.report_public_barrier_field")
    def test_reject_confirmation(
        self,
        mock_report_field,
        mock_barrier_patch,
        mock_add_message,
        mock_patch,
        mock_ready,
    ):
        response = self.client.post(
            reverse(
                "barriers:approve_public_barrier_confirmation",
                kwargs={"barrier_id": self.barrier["id"], "countdown": 17},
            ),
            data={
                "content_clearance": True,
                "external_clearances": True,
                "public_approval_summary": "Test summary",
                "submit_approval": "Set publication status to 'not allowed'",
            },
        )
        assert response.status_code == HTTPStatus.FOUND
        assert mock_ready.called is False
        assert mock_patch.called is True
        assert mock_patch.call_count == 1
        assert mock_report_field.call_count == 2
        assert mock_barrier_patch.call_count == 1

        expected_message_tag = "The publication status is set to: not allowed"
        assert mock_add_message.called is True
        assert expected_message_tag in str(mock_add_message.call_args)


class PublishBarrierConfirmationTestCase(MarketAccessTestCase):
    @patch("utils.api.resources.PublicBarriersResource.publish")
    @patch("django.contrib.messages.add_message")
    def test_publish_confirmation(self, mock_add_message, mock_publish):
        response = self.client.post(
            reverse(
                "barriers:publish_public_barrier_confirmation",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={},
        )
        assert response.status_code == HTTPStatus.FOUND
        assert mock_publish.called is True

        expected_message_tag = "This barrier has been published on GOV.UK"
        assert mock_add_message.called is True
        assert expected_message_tag in str(mock_add_message.call_args)


class UnpublishBarrierConfirmationTestCase(MarketAccessTestCase):
    @patch("utils.api.resources.PublicBarriersResource.unpublish")
    @patch("utils.api.resources.PublicBarriersResource.patch")
    @patch("django.contrib.messages.add_message")
    def test_unpublish_confirmation(self, mock_add_message, mock_patch, mock_unpublish):
        response = self.client.post(
            reverse(
                "barriers:unpublish_public_barrier_confirmation",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={
                "public_publisher_summary": "Test summary",
            },
        )
        assert response.status_code == HTTPStatus.FOUND
        assert mock_unpublish.called is True
        assert mock_patch.called is True

        expected_message_tag = "This barrier has been removed from GOV.UK"
        assert mock_add_message.called is True
        assert expected_message_tag in str(mock_add_message.call_args)

    @patch("utils.api.resources.PublicBarriersResource.unpublish")
    @patch("utils.api.resources.PublicBarriersResource.patch")
    def test_unpublish_confirmation_missing_summary(self, mock_patch, mock_unpublish):
        response = self.client.post(
            reverse(
                "barriers:unpublish_public_barrier_confirmation",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={
                "public_publisher_summary": "",
            },
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert form.is_valid() is False
        assert "public_publisher_summary" in form.errors
        assert mock_unpublish.called is False
        assert mock_patch.called is False


class PublicBarrierActionsTestCase(MarketAccessTestCase):
    @patch("utils.api.resources.PublicBarriersResource.ready_for_approval")
    @patch("utils.api.resources.UsersResource.get_current")
    @patch("users.mixins.UserMixin.get_user")
    @patch("utils.api.client.PublicBarriersResource.get_activity")
    @patch("utils.api.client.PublicBarriersResource.get_notes")
    @patch("django.contrib.messages.add_message")
    def test_submit_for_approval_calls_api(
        self,
        mock_add_message,
        mock_get_notes,
        mock_get_activity,
        mock_get_user,
        mock_user,
        mock_ready_for_approval,
    ):
        mock_get_user.return_value = self.publisher_user
        mock_user.return_value = self.publisher_user
        mock_get_notes.return_value = []
        mock_get_activity.return_value = self.public_barrier_activity
        response = self.client.post(
            reverse(
                "barriers:public_barrier_detail",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={"action": "submit-for-approval"},
        )
        assert response.status_code == HTTPStatus.FOUND
        assert mock_ready_for_approval.called is True

        expected_message_tag = "This barrier is now awaiting approval"
        assert mock_add_message.called is True
        assert expected_message_tag in str(mock_add_message.call_args)

    @patch("utils.api.resources.PublicBarriersResource.allow_for_publishing_process")
    @patch("utils.api.resources.UsersResource.get_current")
    @patch("users.mixins.UserMixin.get_user")
    @patch("utils.api.client.PublicBarriersResource.get_activity")
    @patch("utils.api.client.PublicBarriersResource.get_notes")
    @patch("django.contrib.messages.add_message")
    def test_remove_for_approval_calls_api(
        self,
        mock_add_message,
        mock_get_notes,
        mock_get_activity,
        mock_get_user,
        mock_user,
        mock_allow_for_publishing_process,
    ):
        mock_get_user.return_value = self.publisher_user
        mock_user.return_value = self.publisher_user
        mock_get_notes.return_value = []
        mock_get_activity.return_value = self.public_barrier_activity
        response = self.client.post(
            reverse(
                "barriers:public_barrier_detail",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={"action": "remove-for-approval"},
        )
        assert response.status_code == HTTPStatus.FOUND
        assert mock_allow_for_publishing_process.called is True

        expected_message_tag = "This barrier is not ready for approval"
        assert mock_add_message.called is True
        assert expected_message_tag in str(mock_add_message.call_args)

    @patch("utils.api.resources.PublicBarriersResource.ready_for_approval")
    @patch("utils.api.resources.UsersResource.get_current")
    @patch("users.mixins.UserMixin.get_user")
    @patch("utils.api.client.PublicBarriersResource.get_activity")
    @patch("utils.api.client.PublicBarriersResource.get_notes")
    @patch("django.contrib.messages.add_message")
    def test_revoke_approval_calls_api(
        self,
        mock_add_message,
        mock_get_notes,
        mock_get_activity,
        mock_get_user,
        mock_user,
        mock_ready_for_approval,
    ):
        mock_get_user.return_value = self.publisher_user
        mock_user.return_value = self.publisher_user
        mock_get_notes.return_value = []
        mock_get_activity.return_value = self.public_barrier_activity
        response = self.client.post(
            reverse(
                "barriers:public_barrier_detail",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={"action": "remove-for-publishing"},
        )
        assert response.status_code == HTTPStatus.FOUND
        assert mock_ready_for_approval.called is True

        expected_message_tag = "This barrier needs to be approved again"
        assert mock_add_message.called is True
        assert expected_message_tag in str(mock_add_message.call_args)
