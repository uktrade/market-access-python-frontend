from barriers.constants import PRELIMINARY_ASSESSMENT_CHOICES
from utils.models import APIModel

from .documents import Document


class EconomicAssessment(APIModel):
    _economic_impact_assessments = None
    date_fields = ("archived_on", "created_on", "reviewed_on")

    def __init__(self, data):
        self.data = data
        self.documents = [Document(document) for document in data.get("documents", [])]

    @property
    def archived_economic_impact_assessments(self):
        return [
            assessment
            for assessment in self.economic_impact_assessments
            if assessment.archived is True
        ]

    @property
    def current_economic_impact_assessment(self):
        for assessment in self.economic_impact_assessments:
            if assessment.archived is False:
                return assessment

    @property
    def economic_impact_assessments(self):
        if self._economic_impact_assessments is None:
            self._economic_impact_assessments = [
                EconomicImpactAssessment(assessment)
                for assessment in self.data.get("economic_impact_assessments", [])
            ]
        return self._economic_impact_assessments


class EconomicImpactAssessment(APIModel):
    date_fields = ("archived_on", "created_on")


class ResolvabilityAssessment(APIModel):
    date_fields = ("archived_on", "created_on", "reviewed_on")


class StrategicAssessment(APIModel):
    date_fields = ("archived_on", "created_on", "reviewed_on")


class PreliminaryAssessment(APIModel):
    date_fields = "created_on"

    @property
    def get_value_display(self):
        value = str(self.data.get("value", ""))
        if value:
            return PRELIMINARY_ASSESSMENT_CHOICES[value]
        else:
            return ""
