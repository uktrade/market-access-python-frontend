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
            href=reverse_lazy("reports:report-barrier-wizard"),
            text="Start now",
            button_type="start",
        ),
    )

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["stages"] = {
            "1.1": "to describe the barrier",
            "1.2": "what the status of the is",
            "1.3": "which countries the barrier relates to",
            "1.4": "whether the barrier affects exporting or importing",
            "1.5": "which sectors the barrier affects",
            "1.6": "which companies the barrier affects",
            "1.7": "which goods and services or investments the barrier affects",
        }
        return context_data


class NewReportBarrierAboutView(ReportsFormView):
    heading_text = "About the barrier"
    heading_caption = "Section 1 of 7"
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
