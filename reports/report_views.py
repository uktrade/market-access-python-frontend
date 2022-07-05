from typing import Any, Dict

from django.forms import Form
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import FormView, TemplateView

from barriers.constants import STATUSES
from reports.model_forms.new_report_barrier_about import NewReportBarrierAboutForm
from reports.model_forms.new_report_barrier_location import NewReportBarrierLocationForm
from reports.model_forms.new_report_barrier_status import NewReportBarrierStatusForm
from reports.model_forms.new_report_barrier_summary import NewReportBarrierSummaryForm
from reports.models import Report
from utils.api.client import MarketAccessAPIClient
from utils.exceptions import APIHttpException
from utils.metadata import MetadataMixin


class ReportViewBase(MetadataMixin, TemplateView):
    heading_text = ""
    heading_caption = ""
    _client: MarketAccessAPIClient = None

    success_path = None
    extra_paths = {}
    _barrier: Report = None

    def __init__(self, **kwrags) -> None:
        if kwrags.get("barrier_id"):
            self.barrier = self.get_barrier(kwrags["barrier_id"])
        super().__init__(**kwrags)

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
        try:
            return self.client.reports.get(uuid)
        except APIHttpException as e:
            if e.status_code == 404:
                # Once a report is submitted it becomes a barrier
                # So it can go missing - let's try to find it
                self.get_barrier(uuid)
            else:
                raise

    def get_success_url(self) -> str:
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
        return context_data


class ReportFormViewBase(ReportViewBase, FormView):
    def form_valid(self, form: Form) -> HttpResponse:
        if hasattr(form, "serialize_data"):
            # Certain forms require values to be serialized
            # to be compatible with the Barrier API
            data = form.serialize_data()
        else:
            data = form.cleaned_data
        self._barrier = self.client.reports.patch(self.kwargs["barrier_id"], **data)
        return super().form_valid(form)

    def get_initial(self) -> Dict[str, Any]:
        initial = super().get_initial()
        return {**initial, **self.form_class.get_barrier_initial(self.barrier)}


class ReportDetail(ReportViewBase):
    template_name = "reports/report_detail.html"
    extra_paths = {
        "1.1": "reports:barrier_about",
        "1.2": "reports:barrier_summary",
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
        return context_data

    def get_success_url(self):
        return reverse_lazy(
            "barriers:barrier_detail",
            kwargs={"barrier_id": str(self.form_group.barrier_id)},
        )

    def success(self):
        self.form_group.submit()

    # def get(self, request, *args, **kwargs):
    #     barrier_id = kwargs.get("barrier_id")
    #     self.draft_barrier = self.get_draft_barrier(barrier_id)
    #     if self.draft_barrier:
    #         self.init_view(request, **kwargs)
    #         self.form_group.update_context(self.draft_barrier)
    #         return self.render_to_response(self.get_context_data())
    #     else:
    #         url = reverse_lazy(
    #             "barriers:barrier_detail", kwargs={"barrier_id": barrier_id}
    #         )
    #         return redirect(url, permanent=True)


class NewReportBarrierAboutView(ReportFormViewBase):
    heading_text = "About the barrier"
    heading_caption = "Question 1 of 6"
    template_name = "reports/new_report_barrier_about.html"
    form_class = NewReportBarrierAboutForm
    success_path = "reports:barrier_summary"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # kwargs["tags"] = self.metadata.get_report_tag_choices()
        return kwargs

    def get_initial(self) -> Dict[str, Any]:
        initial = super().get_initial()
        return {**initial, **self.form_class.get_barrier_initial(self.barrier)}

    def set_success_path(self):
        action = self.request.POST.get("action")
        if action == "exit":
            self.success_path = "reports:draft_barrier_details"
        else:
            self.success_path = "reports:barrier_summary"

    # def success(self):
    #     self.form_group.save(payload=self.form_group.prepare_payload_about())
    #     self.set_success_path()


class NewReportBarrierSummaryView(ReportFormViewBase):
    heading_text = "Barrier summary"
    heading_caption = "Question 1 of 6"
    template_name = "reports/new_report_barrier_summary.html"
    form_class = NewReportBarrierSummaryForm
    success_path = "reports:barrier_status"
    # success_path = "reports:draft_barrier_details"
    extra_paths = {"back": "reports:barrier_about"}

    # def get_context_data(self, **kwargs):
    #     context_data = super().get_context_data(**kwargs)
    #     status = self.form_group.status_form.get("status")
    #     context_data["is_resolved"] = status in (
    #         STATUSES.RESOLVED_IN_PART,
    #         STATUSES.RESOLVED_IN_FULL,
    #     )
    #     return context_data

    # def success(self):
    #     self.form_group.save(payload=self.form_group.prepare_payload_summary())
    #     if self.request.POST.get("action") != "exit":
    #         # TODO: Move submit to real last page
    #         # self.form_group.submit()
    #         # self.success_path = reverse(
    #         #     "barriers:barrier_term_uuid",
    #         #     kwargs={"barrier_id": self.form_group.barrier_id},
    #         # )
    #         pass

    # def get_success_url(self):
    #     if self.request.POST.get("action") == "exit":
    #         return super().get_success_url()

    #     return reverse(
    #         "reports:barrier_status_uuid",
    #         kwargs={"barrier_id": self.form_group.barrier_id},
    #     )


class NewReportBarrierStatusView(ReportFormViewBase):
    """
    Report a barrier - Step 1.2
    """

    heading_text = "Barrier status"
    heading_caption = "Question 2 of 6"
    template_name = "reports/new_report_barrier_status.html"
    form_class = NewReportBarrierStatusForm
    success_path = "reports:barrier_location"
    extra_paths = {"back": "reports:barrier_summary"}

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
    template_name = "reports/new_report_barrier_location.html"
    form_class = NewReportBarrierLocationForm
    success_path = None
    extra_paths = {"back": "reports:barrier_status"}

    def get_success_url(self) -> str:
        if self.barrier.country_trading_bloc():
            return reverse_lazy(
                "barriers:barrier_caused_by_trading_bloc_uuid",
                kwargs={"barrier_id": self.form_group.barrier_id},
            )
        return super().get_success_url()

    # def get_form_kwargs(self):
    #     kwargs = super().get_form_kwargs()
    #     kwargs["countries"] = self.metadata.get_country_list()
    #     kwargs["trading_blocs"] = self.metadata.get_trading_bloc_list()
    #     return kwargs

    # def get_initial(self):
    #     form_data = self.form_group.get(self.form_session_key, {})
    #     if form_data.get("country"):
    #         return {"location": form_data["country"]}
    #     elif form_data.get("trading_bloc"):
    #         return {"location": form_data["trading_bloc"]}

    # def post(self, request, *args, **kwargs):
    #     location_form = NewReportBarrierLocationForm(self.get_form_kwargs())
    #     if location_form.is_valid():
    #         has_admin_areas_form = self.form_classes["has_admin_areas"](request.POST)
    #         admin_areas_form = self.form_classes["admin_areas"](request.POST)
    #         trade_direction_form = self.form_classes["trade_direction"](request.POST)

    #     return super().post(request, *args, **kwargs)

    # def success(self):
    #     country_id = self.form_group.location_form["country"]
    #     country_trading_bloc = self.metadata.get_trading_bloc_by_country_id(country_id)
    #     admin_areas = self.metadata.get_admin_areas_by_country(country_id)
    #     if country_trading_bloc:
    #         self.success_path = "reports:barrier_caused_by_trading_bloc"
    #     elif admin_areas:
    #         self.success_path = "reports:barrier_has_admin_areas"
    #     else:
    #         self.success_path = "reports:barrier_trade_direction"
    #         self.form_group.selected_admin_areas = ""


# class NewReportBarrierLocationHasAdminAreasView(ReportFormViewBase):
#     """Does it affect the entire country?"""

#     heading_text = "Location of the barrier"
#     template_name = "reports/new_report_barrier_location_has_admin_areas.html"
#     form_class = NewReportBarrierLocationHasAdminAreasForm
#     success_path = None
#     extra_paths = {"back": "reports:barrier_location"}
#     form_session_key = FormSessionKeys.HAS_ADMIN_AREAS

#     def success(self):
#         has_admin_areas = self.form_group.has_admin_areas["has_admin_areas"]
#         # TODO: perhaps reword "HasAdminAreas" to "AffectsEntireCountry"
#         #   aim for something that reads well like "(affects_entire_country == NO)"
#         if has_admin_areas is HasAdminAreas.NO:
#             if self.form_group.selected_admin_areas:
#                 self.success_path = "reports:barrier_admin_areas"
#             else:
#                 self.success_path = "reports:barrier_add_admin_areas"
#         else:
#             self.success_path = "reports:barrier_trade_direction"
#             self.form_group.selected_admin_areas = ""


# class NewReportBarrierLocationAddAdminAreasView(ReportFormViewBase):
#     """
#     Users can add admin areas that are affected by the barrier.
#     """

#     heading_text = "Location of the barrier"
#     template_name = "reports/new_report_barrier_location_add_admin_areas.html"
#     form_class = NewReportBarrierLocationAddAdminAreasForm
#     success_path = "reports:barrier_admin_areas"
#     extra_paths = {"back": "reports:barrier_has_admin_areas"}
#     form_session_key = FormSessionKeys.ADMIN_AREAS

#     @property
#     def selected_admin_areas(self):
#         """
#         Returns selected admin areas if any as a GENERATOR.
#         :return: TUPLE, (BOOL|has selected admin areas, GENERATOR|selected admin areas)
#         """
#         area_ids = self.form_group.selected_admin_areas
#         choices = (
#             (area["id"], area["name"])
#             for area in self.metadata.get_admin_areas(area_ids)
#         )
#         return (area_ids != ""), choices

#     @property
#     def country_id(self):
#         form_data = self.form_group.location_form
#         return form_data.get("country")

#     def get_context_data(self, **kwargs):
#         context_data = super().get_context_data(**kwargs)
#         has_selected_admin_areas, selected_admin_areas = self.selected_admin_areas
#         context_data["has_selected_admin_areas"] = has_selected_admin_areas
#         context_data["selected_admin_areas"] = selected_admin_areas
#         return context_data

#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()

#         admin_areas = self.metadata.get_admin_areas_by_country(self.country_id)
#         selected_admin_areas = self.form_group.selected_admin_areas

#         kwargs["admin_areas"] = (
#             (admin_area["id"], admin_area["name"])
#             for admin_area in admin_areas
#             if admin_area["id"] not in selected_admin_areas
#         )
#         return kwargs

#     def form_valid(self, form):
#         new_data = form.cleaned_data
#         selected_admin_areas = self.form_group.selected_admin_areas
#         if selected_admin_areas:
#             data = f"{selected_admin_areas}, {new_data['admin_areas']}"
#             self.form_group.selected_admin_areas = data
#         else:
#             self.form_group.selected_admin_areas = new_data["admin_areas"]
#         return super().form_valid(form)


# class NewReportBarrierAdminAreasView(ReportFormViewBase):
#     heading_text = "Location of the barrier"
#     template_name = "reports/new_report_barrier_location_admin_areas.html"
#     success_path = "reports:barrier_trade_direction"
#     extra_paths = {
#         "back": "reports:barrier_add_admin_areas",
#         "remove_admin_area": "reports:barrier_remove_admin_areas",
#     }
#     form_class = NewReportBarrierLocationAdminAreasForm

#     @property
#     def selected_admin_areas(self):
#         choices = (
#             (area["id"], area["name"])
#             for area in self.metadata.get_admin_areas(
#                 self.form_group.selected_admin_areas
#             )
#         )
#         return choices

#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs["admin_areas"] = self.selected_admin_areas
#         return kwargs


# class NewReportBarrierLocationRemoveAdminAreasView(ReportFormViewBase):
#     http_method_names = "post"
#     success_path = "reports:barrier_admin_areas"

#     def post(self, request, *args, **kwargs):
#         self.init_view(request, **kwargs)
#         admin_area_id = request.POST.get("admin_area")
#         self.form_group.remove_selected_admin_area(admin_area_id)
#         return HttpResponseRedirect(self.get_success_url())


# class NewReportBarrierCausedByTradingBlocView(ReportFormViewBase):
#     heading_text = "Location of the barrier"
#     template_name = "reports/new_report_caused_by_trading_bloc.html"
#     form_class = NewReportCausedByTradingBlocForm
#     success_path = None
#     extra_paths = {"back": "reports:barrier_location"}
#     form_session_key = FormSessionKeys.CAUSED_BY_TRADING_BLOC

#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         country_id = self.form_group.location_form.get("country")
#         trading_bloc = self.metadata.get_trading_bloc_by_country_id(country_id)
#         kwargs["trading_bloc"] = trading_bloc
#         return kwargs

#     def success(self):
#         country_id = self.form_group.location_form["country"]
#         country_trading_bloc = self.metadata.get_trading_bloc_by_country_id(country_id)
#         admin_areas = self.metadata.get_admin_areas_by_country(country_id)
#         if admin_areas:
#             self.success_path = "reports:barrier_has_admin_areas"
#         else:
#             self.success_path = "reports:barrier_trade_direction"
#             self.form_group.selected_admin_areas = ""


# class NewReportBarrierTradeDirectionView(ReportFormViewBase):
#     heading_text = "Location of the barrier"
#     template_name = "reports/new_report_barrier_trade_direction.html"
#     form_class = NewReportBarrierTradeDirectionForm
#     extra_paths = {"back": "reports:barrier_location"}
#     form_session_key = FormSessionKeys.TRADE_DIRECTION

#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs["trade_direction_choices"] = self.metadata.get_trade_direction_choices()
#         return kwargs

#     def set_success_path(self):
#         action = self.request.POST.get("action")
#         if action == "exit":
#             self.success_path = "reports:draft_barrier_details"
#         else:
#             self.success_path = "reports:barrier_has_sectors"

#     def success(self):
#         self.form_group.save()
#         self.set_success_path()
