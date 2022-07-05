from django.core.exceptions import ImproperlyConfigured
from django.forms import Form
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, RedirectView, TemplateView
from django.views.generic.base import ContextMixin

from barriers.constants import STATUSES
from barriers.views.commodities import BarrierEditCommodities
from partials.callout import Callout, CalloutButton
from reports.constants import FormSessionKeys
from reports.forms.new_report_barrier_about import NewReportBarrierAboutForm
from reports.forms.new_report_barrier_categories import (
    NewReportBarrierCategoriesAddForm,
    NewReportBarrierCategoriesForm,
)
from reports.forms.new_report_barrier_commodities import (
    NewReportUpdateBarrierCommoditiesForm,
)
from reports.forms.new_report_barrier_location import (
    HasAdminAreas,
    NewReportBarrierLocationAddAdminAreasForm,
    NewReportBarrierLocationAdminAreasForm,
    NewReportBarrierLocationForm,
    NewReportBarrierLocationHasAdminAreasForm,
    NewReportBarrierTradeDirectionForm,
    NewReportCausedByTradingBlocForm,
)
from reports.forms.new_report_barrier_sectors import (
    NewReportBarrierAddSectorsForm,
    NewReportBarrierHasSectorsForm,
    NewReportBarrierSectorsForm,
    SectorsAffected,
)
from reports.forms.new_report_barrier_status import (
    NewReportBarrierStatusForm,
    NewReportBarrierTermForm,
)
from reports.forms.new_report_barrier_summary import NewReportBarrierSummaryForm
from reports.helpers import ReportFormGroup
from utils.api.client import MarketAccessAPIClient
from utils.exceptions import APIHttpException
from utils.metadata import MetadataMixin


class CalloutMixin(ContextMixin):
    callout = None

    def get_callout(self):
        """Returns the callout instance to use or None."""
        if isinstance(self.callout, Callout):
            return self.callout
        else:
            return None

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        callout = self.get_callout
        if callout:
            context_data["callout"] = callout

        return context_data


class ReportBarrierContextMixin(CalloutMixin):
    heading_caption = "Report a barrier"
    heading_text = ""
    back_url = ""
    urls = {}

    def get_heading(self):
        return {
            "caption": self.heading_caption,
            "text": self.heading_text,
        }

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["heading"] = self.get_heading()
        context_data["page"] = "add-a-barrier"
        context_data["urls"] = self.urls
        return context_data


class ReportsTemplateView(MetadataMixin, ReportBarrierContextMixin, TemplateView):
    """A base view for displaying a report template with optional callout."""


class ReportsFormView(MetadataMixin, ReportBarrierContextMixin, FormView):
    """
    A base view for displaying a report template with forms and optional callout.
    If both provided in the view back_path overrides back_url.
    """

    form_class = Form
    is_form_set = False
    form_classes = []
    form_session_key = ""
    form_group = None
    success_path = ""
    back_path = ""
    extra_paths = {}

    @property
    def session_keys(self):
        return self.form_group.session_keys

    def get(self, request, *args, **kwargs):
        self.init_view(request, **kwargs)
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.init_view(request, **kwargs)
        return super().post(request, *args, **kwargs)

    def success(self):
        """To be implemented - method to run when form is valid"""
        pass

    def get_initial(self):
        """
        Returns the initial data to use for forms on this view.
        """
        initial = super().get_initial()
        form_data = self.form_group.get(self.form_session_key, {})
        initial.update(form_data)
        return initial

    def init_view(self, request, **kwargs):
        barrier_id = kwargs.get("barrier_id")
        self.form_group = ReportFormGroup(request.session, barrier_id)
        self.urls = self.get_urls()

    def get_urls(self):
        urls = {}
        for url_name, path in self.extra_paths.items():
            urls[url_name] = self.get_path_url(path)
        if self.request.GET.get("next"):
            urls["back"] = self.request.GET.get("next")
        return urls

    def get_path_url(self, path):
        if self.form_group.barrier_id:
            kwargs = {"barrier_id": str(self.form_group.barrier_id)}
            path += "_uuid"
            url = reverse_lazy(path, kwargs=kwargs)
        else:
            url = reverse_lazy(path)

        return str(url)

    def get_success_url(self):
        """
        Entirely overriding success_url in favour to success_path strings
        to support optional UUIDs in form view urls.
        """
        if not self.success_path:
            raise ImproperlyConfigured("No URL to redirect to. Provide a success_path.")

        if self.request.GET.get("next"):
            return self.request.GET.get("next")

        if self.form_group.barrier_id:
            kwargs = {"barrier_id": str(self.form_group.barrier_id)}
            url = reverse_lazy(f"{self.success_path}_uuid", kwargs=kwargs)
        else:
            url = reverse_lazy(self.success_path)
        return str(url)

    def form_valid(self, form):
        if hasattr(form, "get_api_params"):
            data = form.get_api_params()
        else:
            data = form.cleaned_data

        # raise Exception(data)
        self.form_group.set(self.form_session_key, data)
        self.success()
        return super().form_valid(form)

    def form_invalid(self, form):
        form.initial = form.cleaned_data
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        if self.request.GET.get("next"):
            context_data["has_next"] = True
            context_data["next_url"] = self.request.GET.get("next")
        return context_data


class NewReport(ReportsTemplateView):
    """
    Landing page where users can initiate to report a barrier.
    """

    template_name = "reports/new_report.html"
    callout = Callout(
        heading=(
            "Let us know about a barrier that's affecting a UK business exporting "
            "or importing"
        ),
        text="You can save your information and come back later to complete.",
        button=CalloutButton(
            href=reverse_lazy("reports:barrier_start"),
            text="Start now",
            button_type="start",
        ),
    )

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["stages"] = self.metadata.get_report_stages()
        return context_data


class NewReportStartRedirect(RedirectView):
    """
    Redirect to the first stage of the report.
    """

    _client = None
    draft_barrier = None

    @property
    def client(self):
        if not self._client:
            self._client = MarketAccessAPIClient(self.request.session["sso_token"])
        return self._client

    def create_draft_barrier(self):
        return self.client.reports.create()

    def get_redirect_url(self, *args, **kwargs):
        barrier_id = kwargs.get("barrier_id")
        # if not barrier_id create a draft barrier
        if not barrier_id:
            new_draft_barrier = self.create_draft_barrier()
            barrier_id = new_draft_barrier.id
        return reverse_lazy(
            "reports:barrier_about_uuid", kwargs={"barrier_id": barrier_id}
        )


# Barrier Status Form Views


# class NewReportBarrierTermView(ReportsFormView):
#     """
#     Report a barrier - Step 1.1 Select Barrier Term
#     """

#     heading_text = "Barrier status"
#     template_name = "reports/new_report_barrier_term.html"
#     form_class = NewReportBarrierTermForm
#     success_path = "reports:barrier_status"
#     form_session_key = FormSessionKeys.TERM


class NewReportBarrierStatusView(ReportsFormView):
    """
    Report a barrier - Step 1.2
    """

    heading_text = "Barrier status"
    heading_caption = "Question 2 of 6"
    template_name = "reports/new_report_barrier_status.html"
    form_class = NewReportBarrierStatusForm
    success_path = "reports:barrier_location"
    extra_paths = {"back": "reports:barrier_summary"}
    form_session_key = FormSessionKeys.STATUS

    def get_initial(self):
        """
        Returns the initial data to use for forms on this view.
        """
        initial = super().get_initial()
        form_data = self.form_group.get(self.form_session_key, {})
        # raise Exception(form_data)
        initial.update(form_data)
        return initial

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


# Barrier location form views


class NewReportBarrierLocationView(ReportsFormView):
    heading_text = "Location of the barrier"
    template_name = "reports/new_report_barrier_location.html"
    form_class = NewReportBarrierLocationForm
    form_classes = {
        "location": NewReportBarrierLocationForm,
        "has_admin_areas": NewReportBarrierLocationHasAdminAreasForm,
        "admin_areas": NewReportBarrierLocationAddAdminAreasForm,
        "trade_direction": NewReportBarrierTradeDirectionForm,
    }
    is_form_set = True
    success_path = None
    extra_paths = {"back": "reports:barrier_status"}
    form_session_key = FormSessionKeys.LOCATION

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["countries"] = self.metadata.get_country_list()
        kwargs["trading_blocs"] = self.metadata.get_trading_bloc_list()
        return kwargs

    def get_initial(self):
        form_data = self.form_group.get(self.form_session_key, {})
        if form_data.get("country"):
            return {"location": form_data["country"]}
        elif form_data.get("trading_bloc"):
            return {"location": form_data["trading_bloc"]}

    def post(self, request, *args, **kwargs):
        location_form = NewReportBarrierLocationForm(self.get_form_kwargs())
        if location_form.is_valid():
            has_admin_areas_form = self.form_classes["has_admin_areas"](request.POST)
            admin_areas_form = self.form_classes["admin_areas"](request.POST)
            trade_direction_form = self.form_classes["trade_direction"](request.POST)

        return super().post(request, *args, **kwargs)

    def success(self):
        country_id = self.form_group.location_form["country"]
        country_trading_bloc = self.metadata.get_trading_bloc_by_country_id(country_id)
        admin_areas = self.metadata.get_admin_areas_by_country(country_id)
        if country_trading_bloc:
            self.success_path = "reports:barrier_caused_by_trading_bloc"
        elif admin_areas:
            self.success_path = "reports:barrier_has_admin_areas"
        else:
            self.success_path = "reports:barrier_trade_direction"
            self.form_group.selected_admin_areas = ""


class NewReportBarrierLocationHasAdminAreasView(ReportsFormView):
    """Does it affect the entire country?"""

    heading_text = "Location of the barrier"
    template_name = "reports/new_report_barrier_location_has_admin_areas.html"
    form_class = NewReportBarrierLocationHasAdminAreasForm
    success_path = None
    extra_paths = {"back": "reports:barrier_location"}
    form_session_key = FormSessionKeys.HAS_ADMIN_AREAS

    def success(self):
        has_admin_areas = self.form_group.has_admin_areas["has_admin_areas"]
        # TODO: perhaps reword "HasAdminAreas" to "AffectsEntireCountry"
        #   aim for something that reads well like "(affects_entire_country == NO)"
        if has_admin_areas is HasAdminAreas.NO:
            if self.form_group.selected_admin_areas:
                self.success_path = "reports:barrier_admin_areas"
            else:
                self.success_path = "reports:barrier_add_admin_areas"
        else:
            self.success_path = "reports:barrier_trade_direction"
            self.form_group.selected_admin_areas = ""


class NewReportBarrierLocationAddAdminAreasView(ReportsFormView):
    """
    Users can add admin areas that are affected by the barrier.
    """

    heading_text = "Location of the barrier"
    template_name = "reports/new_report_barrier_location_add_admin_areas.html"
    form_class = NewReportBarrierLocationAddAdminAreasForm
    success_path = "reports:barrier_admin_areas"
    extra_paths = {"back": "reports:barrier_has_admin_areas"}
    form_session_key = FormSessionKeys.ADMIN_AREAS

    @property
    def selected_admin_areas(self):
        """
        Returns selected admin areas if any as a GENERATOR.
        :return: TUPLE, (BOOL|has selected admin areas, GENERATOR|selected admin areas)
        """
        area_ids = self.form_group.selected_admin_areas
        choices = (
            (area["id"], area["name"])
            for area in self.metadata.get_admin_areas(area_ids)
        )
        return (area_ids != ""), choices

    @property
    def country_id(self):
        form_data = self.form_group.location_form
        return form_data.get("country")

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        has_selected_admin_areas, selected_admin_areas = self.selected_admin_areas
        context_data["has_selected_admin_areas"] = has_selected_admin_areas
        context_data["selected_admin_areas"] = selected_admin_areas
        return context_data

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        admin_areas = self.metadata.get_admin_areas_by_country(self.country_id)
        selected_admin_areas = self.form_group.selected_admin_areas

        kwargs["admin_areas"] = (
            (admin_area["id"], admin_area["name"])
            for admin_area in admin_areas
            if admin_area["id"] not in selected_admin_areas
        )
        return kwargs

    def form_valid(self, form):
        new_data = form.cleaned_data
        selected_admin_areas = self.form_group.selected_admin_areas
        if selected_admin_areas:
            data = f"{selected_admin_areas}, {new_data['admin_areas']}"
            self.form_group.selected_admin_areas = data
        else:
            self.form_group.selected_admin_areas = new_data["admin_areas"]
        return super().form_valid(form)


class NewReportBarrierAdminAreasView(ReportsFormView):
    heading_text = "Location of the barrier"
    template_name = "reports/new_report_barrier_location_admin_areas.html"
    success_path = "reports:barrier_trade_direction"
    extra_paths = {
        "back": "reports:barrier_add_admin_areas",
        "remove_admin_area": "reports:barrier_remove_admin_areas",
    }
    form_class = NewReportBarrierLocationAdminAreasForm

    @property
    def selected_admin_areas(self):
        choices = (
            (area["id"], area["name"])
            for area in self.metadata.get_admin_areas(
                self.form_group.selected_admin_areas
            )
        )
        return choices

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["admin_areas"] = self.selected_admin_areas
        return kwargs


class NewReportBarrierLocationRemoveAdminAreasView(ReportsFormView):
    http_method_names = "post"
    success_path = "reports:barrier_admin_areas"

    def post(self, request, *args, **kwargs):
        self.init_view(request, **kwargs)
        admin_area_id = request.POST.get("admin_area")
        self.form_group.remove_selected_admin_area(admin_area_id)
        return HttpResponseRedirect(self.get_success_url())


class NewReportBarrierCausedByTradingBlocView(ReportsFormView):
    heading_text = "Location of the barrier"
    template_name = "reports/new_report_caused_by_trading_bloc.html"
    form_class = NewReportCausedByTradingBlocForm
    success_path = None
    extra_paths = {"back": "reports:barrier_location"}
    form_session_key = FormSessionKeys.CAUSED_BY_TRADING_BLOC

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        country_id = self.form_group.location_form.get("country")
        trading_bloc = self.metadata.get_trading_bloc_by_country_id(country_id)
        kwargs["trading_bloc"] = trading_bloc
        return kwargs

    def success(self):
        country_id = self.form_group.location_form["country"]
        country_trading_bloc = self.metadata.get_trading_bloc_by_country_id(country_id)
        admin_areas = self.metadata.get_admin_areas_by_country(country_id)
        if admin_areas:
            self.success_path = "reports:barrier_has_admin_areas"
        else:
            self.success_path = "reports:barrier_trade_direction"
            self.form_group.selected_admin_areas = ""


class NewReportBarrierTradeDirectionView(ReportsFormView):
    heading_text = "Location of the barrier"
    template_name = "reports/new_report_barrier_trade_direction.html"
    form_class = NewReportBarrierTradeDirectionForm
    extra_paths = {"back": "reports:barrier_location"}
    form_session_key = FormSessionKeys.TRADE_DIRECTION

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["trade_direction_choices"] = self.metadata.get_trade_direction_choices()
        return kwargs

    def set_success_path(self):
        action = self.request.POST.get("action")
        if action == "exit":
            self.success_path = "reports:draft_barrier_details"
        else:
            self.success_path = "reports:barrier_has_sectors"

    def success(self):
        self.form_group.save()
        self.set_success_path()


class NewReportBarrierHasSectorsView(ReportsFormView):
    """Does it affect the entire country?"""

    heading_text = "Sectors affected by the barrier"
    template_name = "reports/new_report_barrier_sectors_main.html"
    form_class = NewReportBarrierHasSectorsForm
    extra_paths = {"back": "reports:barrier_trade_direction"}
    form_session_key = FormSessionKeys.SECTORS_AFFECTED

    def set_success_path(self):
        action = self.request.POST.get("action")
        if action == "exit":
            self.success_path = "reports:draft_barrier_details"
        else:
            if (
                self.form_group.sectors_affected["sectors_affected"]
                == SectorsAffected.YES
            ):
                self.success_path = "reports:barrier_sectors"
            else:
                self.success_path = "reports:barrier_categories"

    def success(self):
        self.form_group.save(payload=self.form_group.prepare_payload_sectors())
        self.set_success_path()


class NewReportBarrierSectorsView(ReportsFormView):
    heading_text = "Sectors affected by the barrier"
    heading_caption = "Question 4 of 6"
    template_name = "reports/new_report_barrier_sectors_manage.html"
    form_class = NewReportBarrierSectorsForm
    success_path = "reports:barrier_about"
    extra_paths = {
        "back": "reports:barrier_has_sectors",
        "add_sector": "reports:barrier_add_sectors",
        "add_all": "reports:barrier_add_all_sectors",
        "remove_sector": "reports:barrier_remove_sector",
    }

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        _, selected_sectors = self.form_group.selected_sectors_generator(self.metadata)
        kwargs["sectors"] = selected_sectors
        return kwargs

    def set_success_path(self):
        action = self.request.POST.get("action")
        if action == "exit":
            self.success_path = "reports:draft_barrier_details"
        else:
            self.success_path = "reports:barrier_categories"

    def success(self):
        self.form_group.save(payload=self.form_group.prepare_payload_sectors())
        self.set_success_path()


class NewReportBarrierSectorsAddView(ReportsFormView):
    heading_text = "Sectors affected by the barrier"
    template_name = "reports/new_report_barrier_sectors_add.html"
    form_class = NewReportBarrierAddSectorsForm
    success_path = "reports:barrier_sectors"
    extra_paths = {
        "back": "reports:barrier_sectors",
    }

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        (
            has_selected_sectors,
            selected_sectors,
        ) = self.form_group.selected_sectors_generator(self.metadata)
        context_data["has_selected_sectors"] = has_selected_sectors
        context_data["selected_sectors"] = selected_sectors
        return context_data

    def get_form_kwargs(self):
        """Add available sector choices to form"""
        kwargs = super().get_form_kwargs()
        selected_sectors = self.form_group.selected_sectors or ""
        available_sectors = (
            (sector["id"], sector["name"])
            for sector in self.metadata.get_sector_list(level=0)
            if sector["id"] not in selected_sectors
        )
        kwargs["sectors"] = available_sectors
        return kwargs

    def form_valid(self, form):
        selected_sectors = self.form_group.selected_sectors
        if not selected_sectors or selected_sectors == "all":
            data = form.cleaned_data["sectors"]
        else:
            data = f"{selected_sectors}, {form.cleaned_data['sectors']}"
        self.form_group.selected_sectors = data
        return super().form_valid(form)


class NewReportBarrierSectorsAddAllView(ReportsFormView):
    http_method_names = "post"
    success_path = "reports:barrier_sectors"

    def post(self, request, *args, **kwargs):
        self.init_view(request, **kwargs)
        self.form_group.selected_sectors = "all"
        return HttpResponseRedirect(self.get_success_url())


class NewReportBarrierSectorsRemoveView(ReportsFormView):
    http_method_names = "post"
    success_path = "reports:barrier_sectors"

    def post(self, request, *args, **kwargs):
        self.init_view(request, **kwargs)
        sector_id = request.POST.get("sector")
        if sector_id == "all":
            self.form_group.selected_sectors = ""
        else:
            self.form_group.remove_selected_sector(sector_id)
        return HttpResponseRedirect(self.get_success_url())


class NewReportBarrierAboutView(ReportsFormView):
    heading_text = "About the barrier"
    heading_caption = "Question 1 of 6"
    template_name = "reports/new_report_barrier_about.html"
    form_class = NewReportBarrierAboutForm
    # extra_paths = {"back": "reports:barrier_sectors"}
    form_session_key = FormSessionKeys.ABOUT

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["tags"] = self.metadata.get_report_tag_choices()
        return kwargs

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        source = self.request.POST.get("source")
        if source == form.BS.OTHER:
            form.fields["other_source"].required = True
        else:
            form.fields["other_source"].required = False
        return form

    def set_success_path(self):
        action = self.request.POST.get("action")
        if action == "exit":
            self.success_path = "reports:draft_barrier_details"
        else:
            self.success_path = "reports:barrier_summary"

    def success(self):
        self.form_group.save(payload=self.form_group.prepare_payload_about())
        self.set_success_path()


class NewReportBarrierSummaryView(ReportsFormView):
    heading_text = "Barrier summary"
    heading_caption = "Question 1 of 6"
    template_name = "reports/new_report_barrier_summary.html"
    form_class = NewReportBarrierSummaryForm
    success_path = "reports:barrier_status"
    success_path = "reports:draft_barrier_details"
    extra_paths = {"back": "reports:barrier_about"}
    form_session_key = FormSessionKeys.SUMMARY

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        status = self.form_group.status_form.get("status")
        context_data["is_resolved"] = status in (
            STATUSES.RESOLVED_IN_PART,
            STATUSES.RESOLVED_IN_FULL,
        )
        return context_data

    def success(self):
        self.form_group.save(payload=self.form_group.prepare_payload_summary())
        if self.request.POST.get("action") != "exit":
            # TODO: Move submit to real last page
            # self.form_group.submit()
            # self.success_path = reverse(
            #     "barriers:barrier_term_uuid",
            #     kwargs={"barrier_id": self.form_group.barrier_id},
            # )
            pass

    def get_success_url(self):
        if self.request.POST.get("action") == "exit":
            return super().get_success_url()

        return reverse(
            "reports:barrier_status_uuid",
            kwargs={"barrier_id": self.form_group.barrier_id},
        )


class NewReportBarrierCategoriesView(ReportsFormView):
    heading_text = "Barrier categories"
    heading_caption = "Question 5 of 6"
    template_name: str = "reports/new_report_barrier_categories_edit.html"
    form_class = NewReportBarrierCategoriesForm
    success_path = "reports:barrier_commodities"
    extra_paths = {
        "add_category": "reports:barrier_categories_add",
        "delete_category": "reports:barrier_categories_delete",
    }
    use_session_categories = False

    def get(self, request, *args, **kwargs):
        # if not self.use_session_categories:
        #     request.session["categories"] = self.barrier.categories
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        self.form_group.refresh_context()

        # raise Exception(self.form_group.categories_form)

        # self.form_group.update_context()
        context_data.update(
            {"categories": self.form_group.categories_form.get("categories")}
        )
        # raise Exception(self.request.session.get("categories"))
        return context_data

    def get_initial(self):
        selected_categories = self.form_group.categories_form.get("categories", [])
        # self.form_group.update_context()
        # categories = self.request.session.get("categories", [])
        return {
            "categories": [category for category in selected_categories],
        }

    # def get_form_kwargs(self):
    #     kwargs = super().get_form_kwargs()
    #     kwargs["barrier_id"] = str(self.kwargs.get("barrier_id"))
    #     kwargs["token"] = self.request.session.get("sso_token")
    #     kwargs["categories"] = self.metadata.get_category_list()
    #     return kwargs

    # def form_valid(self, form):
    #     categories_form = self.form_group.categories_form
    #     selected_category = form.cleaned_data.get("category")
    #     categories_form["categories"] = [selected_category]
    #     self.form_group.categories_form = categories_form
    #     return super().form_valid(form)

    def form_valid(self, form):
        # form.save()
        # try:
        #     del self.request.session["categories"]
        # except KeyError:
        #     pass
        return super().form_valid(form)


class NewReportBarrierCategoriesAddView(ReportsFormView):
    heading_text = "Barrier categories"
    template_name: str = "reports/new_report_barrier_categories_add.html"
    form_class = NewReportBarrierCategoriesAddForm
    success_path = "reports:barrier_categories"
    extra_paths = {
        "add_category": "reports:barrier_categories_add",
        "delete_category": "reports:barrier_categories_delete",
        "back": "reports:barrier_categories",
    }

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        # self.form_group.flush_session_keys()
        context_data.update({"categories": self.get_category_list()})
        return context_data

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["categories"] = self.get_category_list()
        return kwargs

    def get_category_list(self):
        """
        Get a list of all categories excluding any already selected
        """
        selected_category_ids = [
            str(category["id"])
            for category in self.request.session.get("categories", [])
        ]
        return [
            category
            for category in self.metadata.get_category_list()
            if str(category["id"]) not in selected_category_ids
        ]

    def add_category_by_id(self, category_id):
        all_categories = self.metadata.get_category_list()
        category = next(
            (
                category
                for category in all_categories
                if category["id"] == int(category_id)
            ),
            None,
        )
        if not category:
            raise Exception("Category not found")

        currently_selected_categories = self.form_group.categories_form.get(
            "categories", []
        )
        if category in currently_selected_categories:
            return currently_selected_categories
        return [*currently_selected_categories, category]

    def form_valid(self, form):
        categories_form = self.form_group.categories_form
        selected_category_id = form.cleaned_data.get("category")
        selected_categories = self.add_category_by_id(selected_category_id)

        categories_form["categories"] = selected_categories
        # [
        #     selected_category_id,
        #     *categories_form["categories"],
        # ]

        self.form_group.categories_form = categories_form
        self.form_group.save()
        return super().form_valid(form)


class NewReportBarrierCategoriesDeleteView(ReportsFormView):
    template_name = None

    def post(self, request, *args, **kwargs):
        # delete category from get param category_id
        # and redirect to barrier_categories
        self.init_view(request, *args, **kwargs)
        category_id = request.POST.get("category_id")
        self.form_group.delete_category(category_id)
        self.form_group.save()

        return HttpResponseRedirect(
            reverse(
                "reports:barrier_categories_uuid",
                kwargs={"barrier_id": self.form_group.barrier_id},
            )
        )


class NewReportBarrierCommoditiesView(BarrierEditCommodities):
    heading_caption = "Question 6 of 6"
    template_name = "reports/new_report_barrier_commodities.html"
    form_class = NewReportUpdateBarrierCommoditiesForm

    def get_success_url(self):
        return reverse(
            "reports:report_barrier_answers", kwargs={"barrier_id": self.barrier.id}
        )

    def get_barrier(self):
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        barrier_id = self.kwargs.get("barrier_id")
        try:
            return client.reports.get(id=barrier_id)
        except APIHttpException as e:
            raise Exception(e)


# class NewReportViewWithRedirectMixin():
#     def get


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


class ReportDetail(ReportsFormView):
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

    @property
    def client(self):
        if not self._client:
            self._client = MarketAccessAPIClient(self.request.session["sso_token"])
        return self._client

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

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["page"] = "add-a-barrier"
        context_data["report"] = self.draft_barrier
        return context_data

    def get_success_url(self):
        return reverse_lazy(
            "barriers:barrier_detail",
            kwargs={"barrier_id": str(self.form_group.barrier_id)},
        )

    def success(self):
        self.form_group.submit()

    def get(self, request, *args, **kwargs):
        barrier_id = kwargs.get("barrier_id")
        self.draft_barrier = self.get_draft_barrier(barrier_id)
        if self.draft_barrier:
            self.init_view(request, **kwargs)
            self.form_group.update_context(self.draft_barrier)
            return self.render_to_response(self.get_context_data())
        else:
            url = reverse_lazy(
                "barriers:barrier_detail", kwargs={"barrier_id": barrier_id}
            )
            return redirect(url, permanent=True)
