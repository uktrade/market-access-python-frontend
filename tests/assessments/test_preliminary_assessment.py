from http import HTTPStatus

from django.urls import reverse
from mock import Mock, patch

from core.tests import MarketAccessTestCase


class EditPreliminaryAssessmentTestCase(MarketAccessTestCase):

    @patch(
        "utils.api.resources.PreliminaryAssessmentResource.get_preliminary_assessment"
    )
    def test_preliminary_assessment_has_initial_data(
        self, mock_get_preliminary_assessment: Mock
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
        assert (
            form.initial["preliminary_value_details"]
            == self.preliminary_assessment.details
        )

    @patch(
        "utils.api.resources.PreliminaryAssessmentResource.get_preliminary_assessment"
    )
    def test_edit_preliminary_assessment_calls_api(
        self,
        mock_get_preliminary_assessment: Mock,
    ):
        barrier_id = self.barrier["id"]

        url = reverse(
            "barriers:edit_preliminary_assessment",
            kwargs={
                "barrier_id": barrier_id,
            },
        )
        response = self.client.post(
            url,
            data={
                "value": "2",
                "details": "updated description",
            },
        )

        mock_get_preliminary_assessment.assert_called_once_with(barrier_id=barrier_id)
        assert response.status_code == 200
