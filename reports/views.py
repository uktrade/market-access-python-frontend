from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import TemplateView

from utils.api.client import MarketAccessAPIClient


class NewReport(TemplateView):
    """
    Landing page where users can initiate to report a barrier.
    """

    template_name = "reports/new_report.html"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["stages"] = {
            "1": "to describe the barrier",
            "2": "what the status of the barrier is",
            "3": "which countries the barrier relates to",
            "4": "whether the barrier affects exporting or importing",
            "5": "which sectors the barrier affects",
            "6": "which companies the barrier affects",
            "7": "which goods and services or investments the barrier affects",
            "8": "whether the barrier can be published on GOV.UK",
            "9": "to provide a title and summary that are suitable for the public to read",
        }
        return context_data


class DraftBarriers(TemplateView):
    template_name = "reports/draft_barriers.html"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        client = MarketAccessAPIClient(self.request.session["sso_token"])
        reports = client.reports.list(ordering="-created_on")
        context_data["reports"] = reports
        return context_data


class DeleteReport(TemplateView):
    template_name = "reports/delete_report.html"

    def get_template_names(self):
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            return ["reports/modals/delete_report.html"]
        return ["reports/delete_report.html"]

    def get_report(self):
        client = MarketAccessAPIClient(self.request.session["sso_token"])
        return client.reports.get(self.kwargs.get("barrier_id"))

    def get_context_data(self, **kwargs):
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            return {"report": self.get_report()}

        context_data = super().get_context_data(**kwargs)
        context_data["page"] = "draft-barriers"

        client = MarketAccessAPIClient(self.request.session["sso_token"])
        reports = client.reports.list(ordering="-created_on")

        context_data["reports"] = reports
        for report in reports:
            if report.id == str(self.kwargs.get("barrier_id")):
                context_data["report"] = report

        return context_data

    def post(self, request, *args, **kwargs):
        report = self.get_report()

        if report.created_by["id"] == request.session["user_data"]["id"]:
            client = MarketAccessAPIClient(request.session.get("sso_token"))
            client.reports.delete(self.kwargs.get("barrier_id"))

        return HttpResponseRedirect(reverse("reports:draft_barriers"))
