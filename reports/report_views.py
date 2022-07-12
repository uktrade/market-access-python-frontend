from typing import Any, Dict

from django.forms import Form
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, TemplateView

from barriers.constants import STATUSES
from barriers.views.commodities import BarrierEditCommodities
from reports.model_forms.new_report_barrier_about_and_summary import (
    NewReportBarrierAboutAndSummary,
)
from reports.model_forms.new_report_barrier_categories import (
    NewReportBarrierCategoriesAddForm,
    NewReportBarrierCategoriesForm,
)
from reports.model_forms.new_report_barrier_commodities import (
    NewReportUpdateBarrierCommoditiesForm,
)
from reports.model_forms.new_report_barrier_location import (
    NewReportBarrierLocationHybridForm,
    NewReportBarrierTradeDirectionForm,
)
from reports.model_forms.new_report_barrier_sectors import (
    NewReportBarrierAddSectorsForm,
    NewReportBarrierHasSectorsForm,
    NewReportBarrierSectorsForm,
)
from reports.model_forms.new_report_barrier_status import NewReportBarrierStatusForm
from reports.model_forms.new_report_barrier_summary import NewReportBarrierSummaryForm
from reports.models import Report
from utils.api.client import MarketAccessAPIClient
from utils.exceptions import APIHttpException
from utils.metadata import MetadataMixin
from utils.react import form_fields_to_dict


class ReportViewBase(MetadataMixin, TemplateView):
    heading_text = ""
    heading_caption = ""
    _client: MarketAccessAPIClient = None

    success_path = None
    extra_paths = {}
    _barrier: Report = None

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
        if self.success_path:
            return self.get_path_url(self.success_path)
        return super().get_success_url()

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
        context_data["barrier"] = self.get_draft_barrier(self.kwargs["barrier_id"])
        context_data["heading"] = {
            "text": self.heading_text,
            "caption": self.heading_caption,
        }
        context_data["urls"] = self.get_urls()
        context_data["has_next"] = self.request.GET.get("next") is not None
        context_data["next_url"] = self.request.GET.get("next")
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


class ReportDetail(ReportViewBase):
    template_name = "reports/report_detail.html"
    extra_paths = {
        "1.1": "reports:barrier_about",
        "1.2": "reports:barrier_status",
        # "1.3": "reports:barrier_term",
        "1.3": "reports:barrier_location",
        "1.4": "reports:barrier_has_sectors",
        "1.5": "reports:barrier_categories",
        "1.6": "reports:barrier_commodities",
    }
    _client = None
    draft_barrier = None

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["page"] = "add-a-barrier"
        context_data["report"] = self.barrier
        context_data["check_answers_url"] = reverse(
            "reports:report_barrier_answers",
            kwargs={"barrier_id": self.kwargs["barrier_id"]},
        )
        return context_data

    def get_success_url(self):
        return reverse_lazy(
            "barriers:barrier_detail",
            kwargs={"barrier_id": str(self.form_group.barrier_id)},
        )

    def success(self):
        self.form_group.submit()


class NewReportBarrierAboutView(ReportFormViewBase):
    heading_text = "About the barrier"
    heading_caption = "Question 1 of 7"
    template_name = "reports/new_report_barrier_about_and_summary.html"
    form_class = NewReportBarrierAboutAndSummary
    success_path = "reports:barrier_status"
    extra_paths = {
        "back": "reports:draft_barrier_details",
    }


class NewReportBarrierSummaryView(ReportFormViewBase):
    heading_text = "Barrier summary"
    heading_caption = "Question 1 of 7"
    template_name = "reports/new_report_barrier_summary.html"
    form_class = NewReportBarrierSummaryForm
    success_path = "reports:barrier_status"
    # success_path = "reports:draft_barrier_details"
    extra_paths = {"back": "reports:barrier_about"}


class NewReportBarrierStatusView(ReportFormViewBase):
    """
    Report a barrier - Step 1.2
    """

    heading_text = "Barrier status"
    heading_caption = "Question 2 of 7"
    template_name = "reports/new_report_barrier_status.html"
    form_class = NewReportBarrierStatusForm
    success_path = "reports:barrier_location"
    extra_paths = {"back": "reports:barrier_about"}

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        form = context_data["form"]
        context_data.update(
            {
                "OPEN_PENDING_ACTION": STATUSES.OPEN_PENDING_ACTION,
                "valid_status_values": [
                    choice[0] for choice in form.fields["status"].choices
                ],
            }
        )
        return context_data


class NewReportBarrierLocationView(ReportFormViewBase):
    heading_text = "Location of the barrier"
    heading_caption = "Question 3 of 7"
    template_name = "reports/new_report_barrier_location_hybrid.html"
    form_class = NewReportBarrierLocationHybridForm
    success_path = None
    extra_paths = {"back": "reports:barrier_status"}

    def get_react_data(self, context_data):

        form_kwargs = {
            "barrier": self.barrier,
        }

        if self.request.method == "POST":
            form = NewReportBarrierLocationHybridForm(
                data=self.request.POST, **form_kwargs
            )
        else:
            form = NewReportBarrierLocationHybridForm(
                data=self.get_initial(), **form_kwargs
            )

        base_data = {
            "barrier_id": self.barrier.id,
            "method": self.request.method,
            "form_fields": form_fields_to_dict(form),
            "heading": {"caption": self.heading_caption, "text": self.heading_text},
            "countries": self.metadata.get_country_list(),
            "trading_blocs": self.metadata.get_trading_bloc_list(),
            "trade_directions": list(self.metadata.get_trade_direction_choices()),
            "admin_areas": self.metadata.get_admin_area_list(),
        }

        if self.request.method == "POST":
            return {
                **base_data,
                "form_valid": form.is_valid(),
                "form_errors": form.errors,
                "form_data": form.data,
            }

        data = {
            **base_data,
            "form_data": self.get_initial(),
        }
        return data

    def get_form_kwargs(self) -> Dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["barrier"] = self.barrier
        return kwargs

    def form_valid(self, form: Form) -> HttpResponse:
        return super().form_valid(form)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context_data = super().get_context_data(**kwargs)
        context_data["react_data"] = self.get_react_data(context_data)
        return context_data

    def get_success_url(self) -> str:
        return reverse_lazy(
            "reports:barrier_trade_direction_uuid",
            kwargs={"barrier_id": self.barrier.id},
        )


class NewReportBarrierTradeDirectionView(ReportFormViewBase):
    heading_text = "Location of the barrier"
    heading_caption = "Question 4 of 7"
    template_name = "reports/new_report_barrier_trade_direction.html"
    form_class = NewReportBarrierTradeDirectionForm
    extra_paths = {"back": "reports:barrier_location"}
    success_path = "reports:barrier_has_sectors"

    def form_invalid(self, form: NewReportBarrierTradeDirectionForm) -> HttpResponse:
        return super().form_invalid(form)

    def form_valid(self, form: Form) -> HttpResponse:
        return super().form_valid(form)


# Start: Sector views


class NewReportBarrierHasSectorsView(ReportFormViewBase):
    """Does it affect the entire country?"""

    heading_text = "Sectors affected by the barrier"
    heading_caption = "Question 5 of 7"
    template_name = "reports/new_report_barrier_sectors_main.html"
    form_class = NewReportBarrierHasSectorsForm
    extra_paths = {
        "back": "reports:barrier_trade_direction",
        "next_step": "reports:barrier_sectors",
        "skip": "reports:barrier_categories_add_first",
    }
    success_path = "reports:barrier_sectors"

    def get_success_url(self) -> str:
        # If sectors_currently_unknown set to True, the we go to the
        # categories page.
        # Otherise we redirect to the sectors selection page
        if not self.barrier.sectors_affected:
            return reverse_lazy(
                "reports:barrier_categories_add_first_uuid",
                kwargs={"barrier_id": self.barrier.id},
            )
        return reverse_lazy(
            "reports:barrier_sectors_uuid", kwargs={"barrier_id": self.barrier.id}
        )

    def form_valid(self, form: Form) -> HttpResponse:
        # allow get_success_url access to form data
        return super().form_valid(form)


class NewReportBarrierSectorsView(ReportFormViewBase):
    heading_text = "Sectors affected by the barrier"
    heading_caption = "Question 4 of 7"
    template_name = "reports/new_report_barrier_sectors_manage.html"
    form_class = NewReportBarrierSectorsForm
    success_path = "reports:barrier_categories_add_first"
    extra_paths = {
        "back": "reports:barrier_has_sectors",
        "add_sector": "reports:barrier_add_sectors",
        "add_all": "reports:barrier_add_all_sectors",
        "remove_sector": "reports:barrier_remove_sector",
    }

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context_data = super().get_context_data(**kwargs)

        if self.barrier.all_sectors:
            context_data["sectors_list"] = [["all", "All sectors"]]
            context_data["sectors"] = "all"
        else:
            context_data["sectors_list"] = [
                (sector["id"], sector["name"]) for sector in self.barrier.sectors
            ]
            context_data["sectors"] = ",".join(
                [sector["id"] for sector in self.barrier.sectors]
            )
        return context_data

    def form_valid(self, form: Form) -> HttpResponse:
        return super().form_valid(form)
        # return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form: Form) -> HttpResponse:
        return super().form_invalid(form)


class NewReportBarrierSectorsAddView(ReportFormViewBase):
    heading_text = "Sectors affected by the barrier"
    template_name = "reports/new_report_barrier_sectors_add.html"
    form_class = NewReportBarrierAddSectorsForm
    success_path = "reports:barrier_sectors"
    extra_paths = {
        "back": "reports:barrier_sectors",
    }

    def serialize_data(self, form: Form):
        data = super().serialize_data(form)
        sectors = data["sectors"]
        barrier_sectors = [sector["id"] for sector in self.barrier.sectors]
        updated_sectors = list(set(sectors + barrier_sectors))
        return {**data, "sectors": updated_sectors, "all_sectors": False}

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        return context_data

    def form_valid(self, form: Form) -> HttpResponse:
        super().form_valid(form)
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form: Form) -> HttpResponse:
        return super().form_invalid(form)


class NewReportBarrierSectorsAddAllView(ReportFormViewBase):
    http_method_names = "post"
    success_path = "reports:barrier_sectors"

    def post(self, request, *args, **kwargs):
        self.client.reports.patch(self.barrier.id, all_sectors=True, sectors=[])
        return HttpResponseRedirect(self.get_success_url())


class NewReportBarrierSectorsRemoveView(ReportFormViewBase):
    http_method_names = "post"
    success_path = "reports:barrier_sectors"

    def post(self, request, *args, **kwargs):
        sector_id = request.POST.get("sector")
        if sector_id == "all":
            self.client.reports.patch(
                self.kwargs["barrier_id"], **{"all_sectors": False}
            )
        else:
            barrier_sectors = [sector["id"] for sector in self.barrier.sectors]
            barrier_sectors.remove(sector_id)
            self.client.reports.patch(
                self.kwargs["barrier_id"], **{"sectors": barrier_sectors}
            )
        return HttpResponseRedirect(self.get_success_url())


# END Secotrs views


class NewReportBarrierCategoriesView(ReportFormViewBase):
    heading_text = "Barrier categories"
    heading_caption = "Question 5 of 7"
    template_name: str = "reports/new_report_barrier_categories_edit.html"
    form_class = NewReportBarrierCategoriesForm
    success_path = "reports:barrier_commodities"
    extra_paths = {
        "back": "reports:barrier_has_sectors",
        "add_category": "reports:barrier_categories_add",
        "delete_category": "reports:barrier_categories_delete",
    }
    use_session_categories = False

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["categories"] = self.barrier.categories
        context_data["category_ids"] = ",".join(
            [str(category["id"]) for category in self.barrier.categories]
        )
        return context_data

    def form_valid(self, form):
        # form.save()
        # try:
        #     del self.request.session["categories"]
        # except KeyError:
        #     pass
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


class NewReportBarrierCategoriesAddView(ReportFormViewBase):
    heading_text = "Barrier categories"
    heading_caption = "Question 5 of 7"
    template_name: str = "reports/new_report_barrier_categories_add.html"
    form_class = NewReportBarrierCategoriesAddForm
    success_path = "reports:barrier_categories"
    extra_paths = {
        "add_category": "reports:barrier_categories_add",
        "delete_category": "reports:barrier_categories_delete",
        "back": "reports:barrier_categories",
        "back_main_journey": "reports:barrier_has_sectors",
    }

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        # self.form_group.flush_session_keys()
        context_data["is_main_journey"] = kwargs.get("is_main_journey", False)
        context_data.update({"categories": self.metadata.get_category_list()})
        return context_data

    def serialize_data(self, form: Form):
        data = super().serialize_data(form)
        return {"categories": [data["category"]]}


class NewReportBarrierCategoriesDeleteView(ReportFormViewBase):
    template_name = None

    def post(self, request, *args, **kwargs):
        category_id = request.POST.get("category_id")
        existing_categories = [category["id"] for category in self.barrier.categories]
        existing_categories.remove(int(category_id))
        self.client.reports.patch(self.barrier.id, categories=existing_categories)
        return HttpResponseRedirect(
            reverse(
                "reports:barrier_categories_uuid",
                kwargs={"barrier_id": self.barrier.id},
            )
        )


class NewReportBarrierCommoditiesView(BarrierEditCommodities):
    heading_text = "Add HS commodity codes"
    heading_caption = "Question 6 of 7"
    template_name = "reports/new_report_barrier_commodities.html"
    form_class = NewReportUpdateBarrierCommoditiesForm

    def get_success_url(self):
        return reverse(
            "reports:report_barrier_answers", kwargs={"barrier_id": self.barrier.id}
        )

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["heading"] = {
            "text": "Add HS commodity codes",
            "caption": "Question 6 of 7",
        }
        context_data["lookup_form"] = self.get_lookup_form()
        return context_data

    def get_barrier(self):
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        barrier_id = self.kwargs.get("barrier_id")
        try:
            return client.reports.get(id=barrier_id)
        except APIHttpException as e:
            raise Exception(e)

    def post(self, request, *args, **kwargs):
        action = request.POST.get("action")
        if action in ("save-and-continue", "save-and-exit"):
            form = self.get_form()
            if form.is_valid():
                form.save()
                self.clear_session_commodities()
                return HttpResponseRedirect(self.get_success_url())
            else:
                return self.form_invalid(form)

        return super().post(request, *args, **kwargs)
