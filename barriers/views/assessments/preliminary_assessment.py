from django.urls import reverse
from django.views.generic import FormView

from barriers.views.mixins import APIBarrierFormViewMixin
from barriers.forms.assessments.preliminary_assessment import UpdatePreliminaryAssessmentForm


class PreliminaryAssessmentValue(APIBarrierFormViewMixin, FormView):
    template_name = "barriers/assessments/preliminary_assessment.html"
    form_class = UpdatePreliminaryAssessmentForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["token"] = self.request.session.get("sso_token")
        kwargs["barrier"] = self.barrier
        kwargs["preliminary_assessment"] = self.preliminary_assessment
        return kwargs

    def get_initial(self):
        if self.preliminary_assessment:
            return {
                "preliminary_value": self.preliminary_assessment.value,
                "preliminary_value_details": self.preliminary_assessment.details,
            }
        else:
            return

    def get_success_url(self):
        return reverse(
            "barriers:assessment_detail",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )