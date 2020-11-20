from .documents import Document

from utils.models import APIModel

import dateutil.parser


class Assessment(APIModel):
    """
    Wrapper around API assessment data
    """

    def __init__(self, data):
        self.data = data
        self.documents = [Document(document) for document in data["documents"]]


class EconomicAssessment(APIModel):
    _economic_impact_assessments = None

    def __init__(self, data):
        self.data = data
        print(data)

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

    @property
    def created_on(self):
        return dateutil.parser.parse(self.data["created_on"])

    @property
    def reviewed_on(self):
        if self.data.get("reviewed_on"):
            return dateutil.parser.parse(self.data["reviewed_on"])


class EconomicImpactAssessment(APIModel):
    def __init__(self, data):
        self.data = data

    @property
    def created_on(self):
        return dateutil.parser.parse(self.data["created_on"])


class ResolvabilityAssessment(APIModel):
    @property
    def created_on(self):
        return dateutil.parser.parse(self.data["created_on"])

    @property
    def reviewed_on(self):
        if self.data.get("reviewed_on"):
            return dateutil.parser.parse(self.data["reviewed_on"])


class StrategicAssessment(APIModel):
    @property
    def created_on(self):
        return dateutil.parser.parse(self.data["created_on"])

    @property
    def reviewed_on(self):
        if self.data.get("reviewed_on"):
            return dateutil.parser.parse(self.data["reviewed_on"])
