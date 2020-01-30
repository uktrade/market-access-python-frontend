from http import HTTPStatus

from django.urls import reverse

from core.tests import MarketAccessTestCase

from mock import patch


class EmptyAssessmentDetailTestCase(MarketAccessTestCase):
    def test_view(self):
        response = self.client.get(
            reverse(
                'barriers:assessment_detail',
                kwargs={'barrier_id': self.barrier['id']}
            )
        )
        assert response.status_code == HTTPStatus.OK
        assert 'assessment' in response.context
        assert response.context['assessment'] is None
        assert 'barrier' in response.context


class AssessmentDetailTestCase(MarketAccessTestCase):
    def setUp(self):
        self.barrier['has_assessment'] = True
        super().setUp()

    def tearDown(self):
        self.barrier['has_assessment'] = False

    @patch("utils.api.resources.BarriersResource.get_assessment")
    def test_view(self, mock_get_assessment):
        assessment = self.assessments[0]
        mock_get_assessment.return_value = assessment
        response = self.client.get(
            reverse(
                'barriers:assessment_detail',
                kwargs={'barrier_id': self.barrier['id']}
            )
        )
        assert response.status_code == HTTPStatus.OK
        assert response.context['assessment'] == assessment
        assert 'barrier' in response.context
