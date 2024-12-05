from http import HTTPStatus

from django.urls import reverse
from mock import Mock, patch

from core.tests import MarketAccessTestCase


class EditPreliminaryAssessmentTestCase(MarketAccessTestCase):

    @patch("utils.api.resources.PreliminaryAssessmentResource.get_preliminary_assessment")
    def test_preliminary_assessment_has_initial_data(self, mock_get_preliminary_assessment: Mock
    ):
        mock_get_preliminary_assessment.return_value = self.preliminary_assessment
        response = self.client.get(
            reverse(
                "barriers:edit_preliminary_assessment",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
        )
        assert response.status_code == HTTPStatus.OK

        assert "form" in response.context
        form = response.context["form"]
        assert form.initial["preliminary_value"] == self.preliminary_assessment.value
        assert form.initial["preliminary_value_details"] == self.preliminary_assessment.details

    @patch("utils.api.resources.PreliminaryAssessmentResource.patch_preliminary_assessment")
    def test_edit_preliminary_assessment_calls_api(self, mock_patch_preliminary_assessment: Mock):
        mock_patch_preliminary_assessment.return_value = True
        barrier_id = self.barrier["id"]

        url = reverse(
            "barriers:edit_preliminary_assessment",
            kwargs={
                "barrier_id": barrier_id,
            },
        )
        response = self.client.patch(
            url,
            data={
                "value": "2",
                "details": "updated description",
            }
        )

        assert response.status_code == 200
        assert response.url == f"/barriers/{barrier_id}/assessments"

        assert mock_patch_preliminary_assessment.call_args[0][0] == barrier_id
        assert mock_patch_preliminary_assessment.call_args[0][1] == 2
        assert mock_patch_preliminary_assessment.call_args[0][2] == "updated description"

