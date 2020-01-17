from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView
from django.views.generic.base import ContextMixin

from partials.callout import Callout, CalloutButton
from reports.forms.new_report_barrier_status import (
    BarrierStatuses,
    NewReportBarrierProblemStatusForm,
    NewReportBarrierStatus2Form,
)

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
    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["page"] = "add-a-barrier"
        return context_data


class ReportsTemplateView(ReportBarrierContextMixin, TemplateView):
    """A base view for displaying a report template with optional callout."""


class ReportsFormView(ReportBarrierContextMixin, FormView):
    """A base view for displaying a report template with forms and optional callout."""
    form_session_key = None

    def get_form_session_key(self):
        return self.form_session_key

    def get_initial(self):
        """
        Returns the initial data to use for forms on this view.
        """
        initial = super().get_initial()
        form_data = self.request.session.get(self.form_session_key, {})
        initial.update(form_data)
        return initial

    def form_valid(self, form):
        self.request.session[self.form_session_key] = form.cleaned_data
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


class NewReportBarrierStatus1(ReportsFormView):
    """
    Add a barrier - Step 1.1 Select Barrier Type
    """
    template_name = "reports/new_report_barrier_problem_status.html"
    form_class = NewReportBarrierProblemStatusForm
    success_url = reverse_lazy('reports:barrier_status')
    form_session_key = "nr_barrier_problem_status_form_data"

    def get_initial(self):
        """
        Returns the initial data to use for forms on this view.
        """
        initial = super().get_initial()
        form_data = self.request.session.get(self.form_session_key, {})
        initial.update(form_data)
        return initial

    def form_valid(self, form):
        self.request.session[self.form_session_key] = form.cleaned_data
        return super().form_valid(form)


class NewReportBarrierStatus2(ReportsFormView):
    """
    Add a barrier - Step 1.2
    """
    template_name = "reports/new_report_barrier_status.html"
    form_class = NewReportBarrierStatus2Form
    success_url = reverse_lazy('reports:barrier_location')
    form_session_key = "nr_barrier_status_form_data"

    def get_initial(self):
        """
        Returns the initial data to use for forms on this view.
        """
        initial = super().get_initial()
        form_data = self.request.session.get(self.form_session_key, {})
        initial.update(form_data)
        return initial

    def post(self, request, *args, **kwargs):
        form = self.get_form()

        status = request.POST.get("status")
        # Mark relevant subform elements required
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

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        self.request.session[self.form_session_key] = form.cleaned_data
        return super().form_valid(form)


class NewReportBarrierLocation(ReportsFormView):
    template_name = "reports/new_report_barrier_location.html"
    form_class = NewReportBarrierStatus2Form
    # TODO: wrap this view up as per MAR-115


class DraftBarriers(TemplateView):
    template_name = "reports/draft_barriers.html"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        client = MarketAccessAPIClient(self.request.session['sso_token'])
        reports = client.reports.list(ordering="-created_on")
        context_data['page'] = "draft_barriers"
        context_data['watchlists'] =  self.request.session.get_watchlists()
        context_data['reports'] = reports
        return context_data