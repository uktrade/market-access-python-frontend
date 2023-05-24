import json
import logging

from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from formtools.preview import FormPreview
from formtools.wizard.views import NamedUrlSessionWizardView

from reports.report_barrier_forms import (
    BarrierAboutForm,
    BarrierStatusForm,
    BarrierLocationForm,
    BarrierTradeDirectionForm,
    BarrierSectorsAffectedForm,
    BarrierCompaniesAffectedForm,
    BarrierExportTypeForm,
)
from utils.api.client import MarketAccessAPIClient

logger = logging.getLogger(__name__)

# How draft barriers work;
# Clicking 'Report A Barrier'->'Start' creates a barrier in the DB, it has a status of 0, a code and created/modified
# dates & creator it also has an attribute 'draft' that is set to 't'
# this is updated to 'f' once all the needed sections are completeand the report-a-barrier flow is complete.
# Assume draft list is a list based on querying by user-id and 'draft'='t'

# Docs for formWizard
# https://django-formtools.readthedocs.io/en/latest/wizard.html#advanced-wizardview-methods

# process_step is form_wizard method we can use to update stored draft barrier each time a page-form is submitted
# by getting the input details and calling the MarketAccessAPIClient

# Can't use formpreview with formwizard:
# https://forum.djangoproject.com/t/django-form-wizard-preview-before-submission/5582
#  called. The last form page can be a summary of previously entered values (with links back to previous pages)
#  and done() is
# on submitting that last page, done method then updates the API by setting 'draft' to 'f'

# Multiple forms in SessionWizard which we can re-call-upon?
# get_context_data? get_form_initial?


class ReportBarrierWizardView(NamedUrlSessionWizardView, FormPreview):
    form_list = [
        ("barrier-name", BarrierAboutForm),
        ("barrier-status", BarrierStatusForm),
        ("barrier-location", BarrierLocationForm),
        ("barrier-trade-direction", BarrierTradeDirectionForm),
        ("barrier-sectors-affected", BarrierSectorsAffectedForm),
        ("barrier-companies-affected", BarrierCompaniesAffectedForm),
        ("barrier-export-type", BarrierExportTypeForm),
    ]

    def get_template_names(self):
        templates = {
            form_name: f"reports/{form_name.replace('-', '_')}_wizard_step.html"
            for form_name in self.form_list
        }
        return [templates[self.steps.current]]

    def get(self, request, *args, **kwargs):

        """
        At this piont we should check if the user is returning via a draft url and clear the current session
        via self.storage.reset(), get the draft barrier and
        convert the data into step data use self.storage.data to resume the drafting process.
        For legacy drafts we need to populate each step.
        This is cumbersome though and all the fields would need to be mapped to the right step

        We save the whole storage object on 'save and exit' skip to done and check to see
        if it is the last step.
        If it is the last step then we save to barrier as normal if not we save the storage object and barrier
        status as draft

        """

        """
        This renders the form or, if needed, does the http redirects.
        """
        step_url = kwargs.get("step", None)
        draft_barrier_id = kwargs.get("draft_barrier_id", None)
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))

        # Is it resuming a draft barrier
        if draft_barrier_id is not None:
            draft_barrier = client.reports.get(id=draft_barrier_id)
            session_data = draft_barrier.new_report_session_data.strip()
            self.storage.reset()
            self.storage.set_step_data("meta", {"barrier_id": str(draft_barrier_id)})
            if session_data == "":
                # TODO - we coould try and map the legacy data here to the relevant steps
                # Step through the formlist and fields and map to value in legact draft
                # e.g setting barrier title on the first form
                self.storage.set_step_data(
                    "barrier-name", {"title": draft_barrier.title}
                )
                self.storage.current_step = self.steps.first
                return redirect(self.get_step_url(self.steps.current))
            else:
                self.storage.data = json.loads(draft_barrier.new_report_session_data)

            # self.storage.current_step = self.steps.first
            return redirect(self.get_step_url(self.steps.current))

        elif step_url == "skip":
            # Save draft and exit
            client = MarketAccessAPIClient(self.request.session.get("sso_token"))
            # Check to see if it is an existing draft barrier otherwise create
            meta_data = self.storage.data.get("step_data").get("meta", None)
            if meta_data:
                barrier_id = meta_data.get("barrier_id", None)
            else:
                barrier_id = None

            if barrier_id:
                # get draft barrier
                barrier_report = client.reports.get(barrier_id)
            else:
                barrier_report = client.reports.create()

            # We should at least have passed the first step and have a barrier title
            barrier_title_form = self.get_cleaned_data_for_step("barrier-name")
            if barrier_title_form is None:
                # We don't have a barrire title therefore nothing to save
                # Send user to first step
                self.storage.current_step = self.steps.first
                return redirect(self.get_step_url(self.steps.first))

            client.reports.patch(
                id=barrier_report.id,
                **barrier_title_form,
                new_report_session_data=json.dumps(self.storage.data),
            )

            return HttpResponseRedirect(reverse("barriers:dashboard"))

        elif step_url is None:
            if "reset" in self.request.GET:
                self.storage.reset()
                self.storage.current_step = self.steps.first
            if self.request.GET:
                query_string = "?%s" % self.request.GET.urlencode()
            else:
                query_string = ""
            return redirect(self.get_step_url(self.steps.current) + query_string)

        # is the current step the "done" name/view?
        elif step_url == self.done_step_name:
            last_step = self.steps.last
            form = self.get_form(
                step=last_step,
                data=self.storage.get_step_data(last_step),
                files=self.storage.get_step_files(last_step),
            )
            return self.render_done(form, **kwargs)

        # is the url step name not equal to the step in the storage?
        # if yes, change the step in the storage (if name exists)
        elif step_url == self.steps.current:
            # URL step name and storage step name are equal, render!
            form = self.get_form(
                data=self.storage.current_step_data,
                files=self.storage.current_step_files,
            )
            return self.render(form, **kwargs)
        elif step_url in self.get_form_list():
            self.storage.current_step = step_url
            return self.render(
                self.get_form(
                    data=self.storage.current_step_data,
                    files=self.storage.current_step_files,
                ),
                **kwargs,
            )
        # invalid step name, reset to first and redirect.
        else:
            self.storage.current_step = self.steps.first
            return redirect(self.get_step_url(self.steps.first))

    def process_step(self, form):
        return self.get_form_step_data(form)

    def done(self, form_list, form_dict, **kwargs):
        submitted_values = {}
        for form in form_list:
            submitted_values = {**submitted_values, **form.clean()}

        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        # Check to see if it is an existing draft barrier otherwise create
        meta_data = self.storage.data.get("step_data").get("meta", None)

        if meta_data:
            barrier_id = meta_data.get("barrier_id", None)
        else:
            barrier_id = None

        if barrier_id:
            # get draft barrier
            barrier_report = client.reports.get(barrier_id)

        else:
            barrier_report = client.reports.create()

        client.reports.patch(
            id=barrier_report.id,
            new_report_session_data=json.dumps(self.storage.data),
            # draft=False,
            **submitted_values,
        )

        return HttpResponseRedirect(reverse("barriers:dashboard"))
