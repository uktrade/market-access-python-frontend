from django.core.exceptions import ImproperlyConfigured
from django.forms import Form
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, FormView
from django.views.generic.base import ContextMixin

from partials.callout import Callout, CalloutButton
from reports.constants import FormSessionKeys
from reports.forms.new_report_barrier_location import (
    NewReportBarrierLocationForm,
    NewReportBarrierLocationHasAdminAreasForm,
    HasAdminAreas, NewReportBarrierLocationAddAdminAreasForm, NewReportBarrierLocationAdminAreasForm)
from reports.forms.new_report_barrier_sectors import NewReportBarrierSectorsForm
from reports.forms.new_report_barrier_status import (
    BarrierStatuses,
    NewReportBarrierProblemStatusForm,
    NewReportBarrierStatusForm,
)
from reports.helpers import ReportFormGroup

from utils.api_client import MarketAccessAPIClient
from utils.metadata import get_metadata


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
    heading_caption = "Add a barrier"
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


class ReportsTemplateView(ReportBarrierContextMixin, TemplateView):
    """A base view for displaying a report template with optional callout."""


class ReportsFormView(ReportBarrierContextMixin, FormView):
    """
    A base view for displaying a report template with forms and optional callout.
    If both provided in the view back_path overrides back_url.
    """
    form_class = Form
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
        barrier_id = kwargs.get('barrier_id')
        self.form_group = ReportFormGroup(request.session, barrier_id)
        self.urls = self.get_urls()

    def get_urls(self):
        urls = {}
        for url_name, path in self.extra_paths.items():
            urls[url_name] = self.get_path_url(path)
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
        if self.form_group.barrier_id:
            kwargs = {"barrier_id": str(self.form_group.barrier_id)}
            url = reverse_lazy(f"{self.success_path}_uuid", kwargs=kwargs)
        else:
            url = reverse_lazy(self.success_path)
        return str(url)

    def form_valid(self, form):
        self.form_group.set(self.form_session_key, form.cleaned_data)
        self.success()
        return super().form_valid(form)


class NewReport(ReportsTemplateView):
    """
    Landing page where users can initiate to add a barrier.
    """
    template_name = "reports/new_report.html"
    callout = Callout(
        heading="Let us know about a non-tariff barrier to a UK business overseas",
        text="You can save your information and come back later to complete.",
        button=CalloutButton(
            href=reverse_lazy("reports:barrier_problem_status"),
            text="Start now",
            button_type="start",
        )
    )

    metadata = get_metadata()
    extra_context = {
        "stages": metadata.get_report_stages()
    }


class NewReportBarrierProblemStatusView(ReportsFormView):
    """
    Add a barrier - Step 1.1 Select Barrier Type
    """
    heading_text = "Status of the barrier"
    template_name = "reports/new_report_barrier_problem_status.html"
    form_class = NewReportBarrierProblemStatusForm
    success_path = 'reports:barrier_status'
    form_session_key = FormSessionKeys.PROBLEM_STATUS


class NewReportBarrierStatusView(ReportsFormView):
    """
    Add a barrier - Step 1.2
    """
    heading_text = "Status of the barrier"
    template_name = "reports/new_report_barrier_status.html"
    form_class = NewReportBarrierStatusForm
    success_path = 'reports:barrier_location'
    extra_paths = {'back': 'reports:barrier_problem_status'}
    form_session_key = FormSessionKeys.STATUS

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        status = self.request.POST.get("status")
        if status == BarrierStatuses.RESOLVED:
            form.fields["resolved_month"].required = True
            form.fields["resolved_year"].required = True
            form.fields["part_resolved_month"].required = False
            form.fields["part_resolved_year"].required = False
        if status == BarrierStatuses.PARTIALLY_RESOLVED:
            form.fields["part_resolved_month"].required = True
            form.fields["part_resolved_year"].required = True
            form.fields["resolved_month"].required = False
            form.fields["resolved_year"].required = False
        return form


class NewReportBarrierLocationView(ReportsFormView):
    heading_text = "Location of the barrier"
    template_name = "reports/new_report_barrier_location.html"
    form_class = NewReportBarrierLocationForm
    success_path = None
    extra_paths = {'back': 'reports:barrier_status'}
    form_session_key = FormSessionKeys.LOCATION
    metadata = get_metadata()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["countries"] = self.metadata.get_country_choices()
        return kwargs

    def form_valid(self, form):
        country_id = form.cleaned_data["country"]
        admin_areas = self.metadata.get_admin_areas_by_country(country_id)
        if admin_areas:
            self.success_path = "reports:barrier_has_admin_areas"
        else:
            self.success_path = "reports:barrier_has_sectors"
            self.form_group.save()

        return super().form_valid(form)


class NewReportBarrierLocationHasAdminAreasView(ReportsFormView):
    """Does it affect the entire country?"""
    heading_text = "Location of the barrier"
    template_name = "reports/new_report_barrier_location_has_admin_areas.html"
    form_class = NewReportBarrierLocationHasAdminAreasForm
    success_path = None
    extra_paths = {'back': 'reports:barrier_location'}
    form_session_key = FormSessionKeys.HAS_ADMIN_AREAS

    def form_valid(self, form):
        has_admin_areas = form.cleaned_data["has_admin_areas"]
        # TODO: perhaps reword "HasAdminAreas" to "AffectsEntireCountry"
        #   aim for something that reads well like "(affects_entire_country == NO)"
        if has_admin_areas is HasAdminAreas.NO:
            if self.form_group.selected_admin_areas:
                self.success_path = "reports:barrier_admin_areas"
            else:
                self.success_path = "reports:barrier_add_admin_areas"
        else:
            self.success_path = "reports:barrier_has_sectors"
            self.form_group.selected_admin_areas = ""
            self.form_group.save()

        return super().form_valid(form)


class NewReportBarrierLocationAddAdminAreasView(ReportsFormView):
    """
    Users can add admin areas that are affected by the barrier.
    """
    heading_text = "Location of the barrier"
    template_name = "reports/new_report_barrier_location_add_admin_areas.html"
    form_class = NewReportBarrierLocationAddAdminAreasForm
    success_path = "reports:barrier_admin_areas"
    extra_paths = {'back': 'reports:barrier_has_admin_areas'}
    form_session_key = FormSessionKeys.ADMIN_AREAS
    metadata = get_metadata()

    @property
    def selected_admin_areas(self):
        """
        Returns selected admin areas if any as a GENERATOR.
        :return: TUPLE, (BOOL|has selected admin areas, GENERATOR|selected admin areas)
        """
        area_ids = self.form_group.selected_admin_areas
        admin_areas = (a["id"] for a in self.metadata.get_admin_areas(area_ids))
        choices = (
            (area["id"], area["name"])
            for area in self.metadata.get_admin_areas(admin_areas)
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
        available_admin_areas = []
        admin_areas = self.metadata.get_admin_area_choices(self.country_id)
        selected_admin_areas = self.form_group.selected_admin_areas or ()

        for area in admin_areas:
            # expecting area to be a tuple - (area_id, area_name)
            if area[0] not in selected_admin_areas:
                available_admin_areas.append(area)

        kwargs["admin_areas"] = available_admin_areas
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
    extra_paths = {
        'back': 'reports:barrier_add_admin_areas',
        'remove_admin_area': 'reports:barrier_remove_admin_areas'
    }
    form_class = NewReportBarrierLocationAdminAreasForm
    metadata = get_metadata()

    @property
    def selected_admin_areas(self):
        area_ids = self.form_group.selected_admin_areas
        admin_areas = (a["id"] for a in self.metadata.get_admin_areas(area_ids))
        choices = (
            (area["id"], area["name"])
            for area in self.metadata.get_admin_areas(admin_areas)
        )
        return choices

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["admin_areas"] = self.selected_admin_areas
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


class NewReportBarrierLocationRemoveAdminAreasView(ReportsFormView):
    http_method_names = 'post'
    success_path = 'reports:barrier_admin_areas'

    def post(self, request, *args, **kwargs):
        self.init_view(request, **kwargs)
        admin_area_id = request.POST.get("admin_area")
        self.form_group.remove_selected_admin_area(admin_area_id)
        return HttpResponseRedirect(self.get_success_url())


class NewReportBarrierSectorsView(ReportsFormView):
    """Does it affect the entire country?"""
    heading_text = "Sectors affected by the barrier"
    template_name = "reports/new_report_barrier_sectors.html"
    form_class = NewReportBarrierSectorsForm
    extra_paths = {'back': 'reports:barrier_location'}


class DraftBarriers(TemplateView):
    template_name = "reports/draft_barriers.html"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        client = MarketAccessAPIClient(self.request.session['sso_token'])
        reports = client.reports.list(ordering="-created_on")
        context_data['page'] = "draft-barriers"
        context_data['watchlists'] = self.request.session.get_watchlists()
        context_data['reports'] = reports
        return context_data


class DeleteReport(TemplateView):
    template_name = "reports/delete_report.html"

    def get_template_names(self):
        if self.request.is_ajax():
            return ["reports/modals/delete_report.html"]
        return ["reports/delete_report.html"]

    def get_report(self):
        client = MarketAccessAPIClient(self.request.session['sso_token'])
        return client.reports.get(self.kwargs.get('report_id'))

    def get_context_data(self, **kwargs):
        if self.request.is_ajax():
            return {'report': self.get_report()}

        context_data = super().get_context_data(**kwargs)
        context_data['page'] = "draft-barriers"

        client = MarketAccessAPIClient(self.request.session['sso_token'])
        reports = client.reports.list(ordering="-created_on")

        context_data['reports'] = reports
        for report in reports:
            if report.id == str(self.kwargs.get('report_id')):
                context_data['report'] = report

        return context_data

    def post(self, request, *args, **kwargs):
        report = self.get_report()

        if report.created_by['id'] == request.session['user_data']['id']:
            client = MarketAccessAPIClient(request.session.get('sso_token'))
            client.reports.delete(self.kwargs.get('report_id'))

        return HttpResponseRedirect(reverse('reports:draft_barriers'))


class ReportDetail(TemplateView):
    template_name = "reports/report_detail.html"

    def get_report(self):
        client = MarketAccessAPIClient(self.request.session['sso_token'])
        return client.reports.get(self.kwargs.get('barrier_id'))

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['page'] = "add-a-barrier"
        context_data['report'] = self.get_report()
        return context_data
