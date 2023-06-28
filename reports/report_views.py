from typing import Any, Dict

from django.forms import Form
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, TemplateView

from barriers.views.commodities import BarrierEditCommodities
from reports.model_forms.new_report_barrier_commodities import (
    NewReportUpdateBarrierCommoditiesForm,
)
from reports.models import Report
from utils.api.client import MarketAccessAPIClient
from utils.exceptions import APIHttpException
from utils.metadata import MetadataMixin
from utils.react import form_fields_to_dict


class ReportURLHandlingMixin:
    """
    Mixin that handles special URLs such as save and exit and save and go to summary
    Back links and next links are handled by the get_urls method
    Note: This is separated into a Mixin to share use with Views that conflict with other
    behaviour
    """

    success_path = None
    extra_paths = {}
    _barrier = None

    def get_next_step_url(self):
        # if save and exit or save and go to summary
        # is not in the form, this is called to get the next
        # step in the process
        # we have a separate method so we can override it without
        # needing to rewrite the exit and summary logic
        if self.success_path:
            return self.get_path_url(self.success_path)
        return super().get_success_url()

    def get_success_url(self) -> str:
        action = self.request.POST.get("action")
        if action == "save-and-exit":
            # Save and exit should send to the detail view
            return reverse(
                "reports:draft_barrier_details_uuid",
                kwargs={"barrier_id": self.kwargs["barrier_id"]},
            )
        if action == "save-and-go-to-summary":
            return reverse(
                "reports:report_barrier_answers",
                kwargs={
                    "barrier_id": self.kwargs["barrier_id"],
                },
            )
        return self.get_next_step_url()

    def get_urls(self):
        urls = {}
        for url_name, path in self.extra_paths.items():
            urls[url_name] = self.get_path_url(path)
        if self.request.GET.get("next"):
            urls["back"] = self.request.GET.get("next")
        return urls

    def get_path_url(self, path):
        return reverse(f"{path}_uuid", kwargs={"barrier_id": self.kwargs["barrier_id"]})

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context_data = super().get_context_data(**kwargs)
        context_data["urls"] = self.get_urls()
        context_data["has_next"] = self.request.GET.get("next") is not None
        context_data["next_url"] = self.request.GET.get("next")
        return context_data


class ReportBarrierMixin:
    _barrier: Report = None
    _client: MarketAccessAPIClient = None

    def __init__(self, *args, **kwrags) -> None:
        if kwrags.get("barrier_id"):
            self.barrier = self.get_barrier(kwrags["barrier_id"])
        super().__init__(*args, **kwrags)

    @property
    def client(self):
        if not self._client:
            self._client = MarketAccessAPIClient(self.request.session["sso_token"])
        return self._client

    @property
    def barrier(self):
        if not self._barrier:
            self._barrier = self.get_draft_barrier(self.kwargs["barrier_id"])
        return self._barrier

    def get_barrier(self, uuid):
        """Once a report is submitted it becomes a barrier"""
        barrier = self.client.barriers.get(uuid)
        return barrier

    def get_draft_barrier(self, uuid):
        return self.client.reports.get(uuid)


class ReportViewBase(
    ReportURLHandlingMixin, ReportBarrierMixin, MetadataMixin, TemplateView
):
    heading_text = ""
    heading_caption = ""
    _client: MarketAccessAPIClient = None

    _barrier: Report = None

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context_data = super().get_context_data(**kwargs)
        context_data["barrier"] = self.get_draft_barrier(self.kwargs["barrier_id"])
        context_data["heading"] = {
            "text": self.heading_text,
            "caption": self.heading_caption,
        }
        return context_data


class ReportFormViewBase(ReportViewBase, FormView):
    def serialize_data(self, form: Form):
        # Serialize the form data to a dict
        # Override if you need to alter the serialized data from the form
        if hasattr(form, "serialize_data"):
            # Certain forms require values to be serialized
            # to be compatible with the Barrier API
            data = form.serialize_data()
        else:
            data = form.cleaned_data
        return data

    def get_form_kwargs(self) -> Dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["barrier"] = self.barrier
        return kwargs

    def form_valid(self, form: Form) -> HttpResponse:
        data = self.serialize_data(form)
        self._barrier = self.client.reports.patch(self.kwargs["barrier_id"], **data)
        return super().form_valid(form)

    def form_invalid(self, form: Form) -> HttpResponse:
        return super().form_invalid(form)

    def get_initial(self) -> Dict[str, Any]:
        initial = super().get_initial()
        if self.request.method == "POST":
            # initial.update(self.request.POST)
            return initial
        return {**initial, **self.form_class.get_barrier_initial(self.barrier)}
