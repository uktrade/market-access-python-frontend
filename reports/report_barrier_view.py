import datetime
import json
import logging

from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from formtools.preview import FormPreview
from formtools.wizard.views import NamedUrlSessionWizardView

from barriers.constants import REPORTABLE_STATUSES, UK_COUNTRY_ID
from barriers.forms.commodities import CommodityLookupForm
from barriers.models import Barrier
from reports.report_barrier_forms import (
    BarrierAboutForm,
    BarrierCompaniesAffectedForm,
    BarrierDetailsSummaryForm,
    BarrierExportTypeForm,
    BarrierLocationForm,
    BarrierPublicEligibilityForm,
    BarrierPublicInformationGateForm,
    BarrierPublicSummaryForm,
    BarrierPublicTitleForm,
    BarrierSectorsAffectedForm,
    BarrierStatusForm,
    BarrierTradeDirectionForm,
)
from utils.api.client import MarketAccessAPIClient
from utils.metadata import MetadataMixin

logger = logging.getLogger(__name__)

# Report-A-Barrier journey uses formtools wizard to provide multi-step form so users can
# enter required data for a new barrier to be added to the DB, and edited/searchable by
# other users.
#
# Docs for formWizard:
# https://django-formtools.readthedocs.io/en/latest/wizard.html#advanced-wizardview-methods
#
# We use formtools session data to hold entered data between steps. This session data
# is saved to the barrier in the DB when user selects to save and exit the process. It is
# also saved to the barrier in the DB when moving to the next step of the multi-part form.
#
# Data is validated and put into the correct format for DB entry in the clean method of
# each form.
#
# Final done method called when submitting the final form page. This method patches the
# data from each step before calling the submit method in the API - which will perform
# further validation and update the barriers "is_draft" value to false, making the barrier
# visible to other users.


def check_public_form_form_display(step):
    """
    Checks the current step, verifies that the prerequisite questions to 'unlock' the next page are met,
    then returns true or false to decide if it should be shown. Wrapping the method allows parameters
    to be sent through the condition dictionary.
    Paths:
    public-eligibility = F -> details-summary
    public-eligibility = T -> public-information-gate = F -> details-summary
    public-eligibility = T -> public-information-gate = T -> public-title -> public-summary -> details-summary
    """

    def _show_form_page(wizard):
        # Get the form data for pages which result in branches
        cleaned_data_eligibility = wizard.get_cleaned_data_for_step(
            "barrier-public-eligibility"
        )
        cleaned_data_information_gate = wizard.get_cleaned_data_for_step(
            "barrier-public-information-gate"
        )

        # Setting the default to show the pages - the 'true' path should pass the longer branch
        show_page = True

        # Check public-eligibility answer to skip to final step if negative answer recieved
        if cleaned_data_eligibility is not None:
            if cleaned_data_eligibility["public_eligibility"] is False:
                show_page = False

        # Check public-information-gate answer only if we are on the public-title or public-summary steps
        # Skip to the final step if a negative answer recieved
        if step in ["public_title", "public_summary"]:
            if cleaned_data_information_gate is not None:
                if cleaned_data_information_gate["public_information"] == "false":
                    show_page = False

        return show_page

    return _show_form_page


class ReportBarrierWizardView(MetadataMixin, NamedUrlSessionWizardView, FormPreview):
    form_list = [
        ("barrier-about", BarrierAboutForm),
        ("barrier-status", BarrierStatusForm),
        ("barrier-location", BarrierLocationForm),
        ("barrier-trade-direction", BarrierTradeDirectionForm),
        ("barrier-sectors-affected", BarrierSectorsAffectedForm),
        ("barrier-companies-affected", BarrierCompaniesAffectedForm),
        ("barrier-export-type", BarrierExportTypeForm),
        ("barrier-public-eligibility", BarrierPublicEligibilityForm),
        ("barrier-public-information-gate", BarrierPublicInformationGateForm),
        ("barrier-public-title", BarrierPublicTitleForm),
        ("barrier-public-summary", BarrierPublicSummaryForm),
        ("barrier-details-summary", BarrierDetailsSummaryForm),
    ]

    # Use a condition dict to indicate pages that may not load depending on branching
    # paths through the form. Call the method outside the class which will return a bool
    # to decide if the page should be included in the form_list.
    condition_dict = {
        "barrier-public-information-gate": check_public_form_form_display(
            "public_information_gate"
        ),
        "barrier-public-title": check_public_form_form_display("public_title"),
        "barrier-public-summary": check_public_form_form_display("public_summary"),
    }

    def get_template_names(self):
        return [f"reports/{self.steps.current.replace('-', '_')}_wizard_step.html"]

    def get(self, request, *args, **kwargs):
        """
        At this point we should check if the user is returning via a draft url and clear
        the current session via self.storage.reset(), get the draft barrier and
        convert the data into step data using self.storage.data to resume the drafting process.

        For legacy drafts we need to populate each step.
        This is cumbersome though and all the fields would need to be mapped to the right step.

        We save the whole storage object on 'save and exit' skip to done and check to see
        if it is the last step.
        If it is the last step then we save to barrier as normal if not we save
        the storage object and barrier status as draft.

        If it is the last step then we save to barrier as normal if not we save the storage object and barrier
        status as draft

        This renders the form or, if needed, does the http redirects.
        """

        step_url = kwargs.get("step", None)
        self.client = MarketAccessAPIClient(self.request.session.get("sso_token"))

        # Handle legacy React app calls
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return self.ajax(request, *args, **kwargs)

        # Is it resuming a draft barrier
        if draft_barrier_id := kwargs.get("draft_barrier_id", None):
            draft_barrier = self.client.reports.get(id=draft_barrier_id)
            session_data = draft_barrier.new_report_session_data.strip()
            self.storage.reset()
            self.storage.set_step_data("meta", {"barrier_id": str(draft_barrier_id)})

            if session_data == "":
                # TODO - we could try and map the legacy data here to the relevant steps
                # Step through the formlist and fields and map to value in legact draft
                # e.g setting barrier title on the first form
                self.storage.set_step_data(
                    "barrier-name", {"title": draft_barrier.title}
                )
                self.storage.current_step = self.steps.first
            else:
                self.storage.data = json.loads(draft_barrier.new_report_session_data)

            return redirect(self.get_step_url(self.steps.current))

        elif step_url == "skip":
            # Save the previously entered data
            self.save_report_progress()

            # Clear the cache for new report
            self.storage.reset()

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

        # Is the current step the "done" name/view?
        elif step_url == self.done_step_name:
            last_step = self.steps.last
            form = self.get_form(
                step=last_step,
                data=self.storage.get_step_data(last_step),
                files=self.storage.get_step_files(last_step),
            )
            return self.render_done(form, **kwargs)

        # Is the url step name not equal to the step in the storage?
        # if yes, change the step in the storage (if name exists)
        elif step_url == self.steps.current:
            # When passing into the step, we need to save our previously entered
            # data.
            self.save_report_progress()

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
        # Invalid step name, reset to first and redirect.
        else:
            self.storage.current_step = self.steps.first
            return redirect(self.get_step_url(self.steps.first))

    def ajax(self, request, *args, **kwargs):
        if request.GET.get("code"):
            selected_location = self.get_default_location()

            lookup_form = CommodityLookupForm(
                initial={"location": UK_COUNTRY_ID},
                data=self.request.GET.dict() or None,
                token=self.request.session.get("sso_token"),
                locations=[
                    {"id": selected_location[0], "name": selected_location[1]},
                    {"id": UK_COUNTRY_ID, "name": "United Kingdom"},
                ],
            )

            if lookup_form.is_valid():
                return JsonResponse(
                    {
                        "status": "ok",
                        "data": lookup_form.get_commodity_data(),
                    }
                )
            else:
                return JsonResponse(
                    {"status": "error", "message": "Enter a real HS commodity code"}
                )
        else:
            return JsonResponse({"status": "error", "message": "Bad request"})

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)

        barrier_id = self.storage.data.get("meta", {}).get("barrier_id", None)
        context["barrier_id"] = barrier_id

        if self.steps.current == "barrier-sectors-affected":
            sectors = [
                (sector["id"], sector["name"])
                for sector in self.metadata.get_sector_list(level=0)
            ]
            context.update({"sectors_list": sectors})

        if self.steps.current == "barrier-export-type":

            confirmed_commodities_data = []

            export_data = self.get_cleaned_data_for_step("barrier-export-type")

            if export_data:
                if export_data["commodities"]:
                    # User has entered HS codes previously
                    # so we need to display these
                    hs6_session_codes = [
                        commodity["code"][:6].ljust(10, "0")
                        for commodity in export_data["commodities"]
                    ]
                    commodity_lookup = {
                        commodity.code: commodity
                        for commodity in self.client.commodities.list(
                            codes=",".join(hs6_session_codes)
                        )
                    }

                    barrier_commodities = []
                    for commodity_data in export_data["commodities"]:
                        code = commodity_data.get("code")
                        hs6_code = code[:6].ljust(10, "0")
                        commodity = commodity_lookup.get(hs6_code)

                        # If commodity exists, format the information so HS component can interpret correctly
                        if commodity:
                            # Frontend component needs JSON compatible country information, we only have the
                            # code, so we need to get the country/bloc object from metadata
                            country_location = {}
                            trading_bloc_location = {}
                            if commodity_data.get("country"):
                                # location is a country
                                country_location = self.metadata.get_country(
                                    commodity_data.get("country")
                                )
                            else:
                                # location is a trading bloc
                                trading_bloc_location = self.metadata.get_trading_bloc(
                                    commodity_data.get("trading_bloc")
                                )

                            # Create dictionary object to contain information, push to array to pass to JS component
                            commodity_obj = {
                                "code": code,
                                "code_display": commodity.code_display,
                                "commodity": commodity.data,
                                "country": country_location,
                                "trading_bloc": trading_bloc_location,
                            }
                            barrier_commodities.append(commodity_obj)

                    confirmed_commodities_data = barrier_commodities

            context.update({"confirmed_commodities_data": confirmed_commodities_data})

        if (
            self.steps.current == "barrier-public-title"
            or self.steps.current == "barrier-public-summary"
        ):
            barrier_internal_data = self.get_cleaned_data_for_step("barrier-about")
            context["internal_title"] = barrier_internal_data["title"]
            context["internal_summary"] = barrier_internal_data["summary"]

        # Put cleaned data into context for the details summary final step
        if self.steps.current == "barrier-details-summary":
            for step in self.storage.data["step_data"]:
                for key, value in self.get_cleaned_data_for_step(step).items():
                    # Some keys will need formatting to be front-end friendly
                    # while they are currently database friendly.
                    if key == "status":
                        # Barrier status - currently a number, need to turn it to the word representation
                        # We can get this from the choice object used in the form
                        for choice in REPORTABLE_STATUSES:
                            if value in choice:
                                context[key] = choice[1]

                    elif key == "country" or key == "trading_bloc":
                        # Barrier location - currently country/bloc UUID/id, need to get country/bloc name
                        # Can use the metadata methods to get this information from given UUID
                        country_details = self.metadata.get_country(value)
                        trading_bloc_details = self.metadata.get_trading_bloc(value)
                        if country_details is not None:
                            context["barrier_location"] = country_details["name"]
                        elif trading_bloc_details is not None:
                            context["barrier_location"] = trading_bloc_details["name"]
                        else:
                            continue

                    elif key == "trade_direction":
                        # Trade direction - currently all caps - needs to be readble version
                        # Use long readable values - same as options in form question
                        if value == "1":
                            context[key] = "Exporting from the UK or investing overseas"
                        else:
                            context[key] = "Importing or investing into the UK"

                    elif key == "main_sector":
                        # Main sector affected - currently sector UUID, needs to be readble name
                        # Can use metadata method to get name
                        sector_information = self.metadata.get_sector(value)
                        context[key] = sector_information["name"]

                    elif key == "sectors":
                        # Other sectors affected - currently list of UUIDs, needs to be readable names list
                        # Can use metadata method to get list of names
                        other_sector_names = []
                        other_sectors_information = self.metadata.get_sectors_by_ids(
                            value
                        )
                        for sector in other_sectors_information:
                            other_sector_names.append(sector["name"])
                        context[key] = other_sector_names

                    elif key == "companies" or key == "related_organisations":
                        # Name of companies - currently list of dictionaries, needs to be readable names list
                        company_names = []
                        for company in value:
                            company_names.append(company["name"])
                        context[key] = company_names

                    elif key == "codes":
                        # HS Codes - currently list of IDs, needs to be list of commodity details
                        # Get the 10 digit code from the given 6 digit codes
                        if value:
                            hs6_codes = []
                            for commodity_code in value:
                                hs6_code = commodity_code[:6].ljust(10, "0")
                                hs6_codes.append(hs6_code)

                            # Query the api for the full details of the list of 10 digit codes
                            commodities_details = self.client.commodities.list(
                                codes=",".join(hs6_codes)
                            )

                            # Build a context data list, eliminating any duplicates retrieved in the api call
                            commodity_context_data = []
                            for commodity in commodities_details:
                                commodity_object = {
                                    "code": commodity.code,
                                    "description": commodity.description,
                                }
                                if commodity_object not in commodity_context_data:
                                    commodity_context_data.append(commodity_object)

                            context[key] = commodity_context_data
                        else:
                            # If no HS codes provided (it is an optional field) set context as empty list
                            context[key] = []

                    elif key == "public_eligibility":
                        # Public eligibility value comes through as 'true' or 'false, needs to have
                        # a readable version for the summary page.
                        context[key] = (
                            "Can be published, once approved"
                            if value
                            else "Cannot be published"
                        )

                    elif key == "title" and step == "barrier-public-title":
                        # Public title and internal title have the same key so need to differentiate in context
                        context["public_title"] = value

                    elif key == "summary" and step == "barrier-public-summary":
                        # Public summary and internal summary have the same key so need to differentiate in context
                        context["public_summary"] = value

                    else:
                        context[key] = value

        return context

    def process_step(self, form):
        """
        This method is used to postprocess the form data. By default, it
        returns the raw `form.data` dictionary.
        """

        # During the process, get_cleaned_data_for_step will trigger an error
        # if some optional forms have been submitted, then later the user chooses a different path.
        # At the root of the branching paths, we need to remove step data if we jump to a different path
        # so we do not cause a keyerror when looping cleaned_data on the final barrier summary step.
        if (
            form.prefix == "barrier-public-eligibility"
            and not form.cleaned_data["public_eligibility"]
        ):
            for form_name in [
                "barrier-public-information-gate",
                "barrier-public-title",
                "barrier-public-summary",
            ]:
                if form_name in self.storage.data["step_data"]:
                    self.storage.data["step_data"].pop(form_name)
        if (
            form.prefix == "barrier-public-information-gate"
            and form.cleaned_data["public_information"] == "false"
        ):
            for form_name in ["barrier-public-title", "barrier-public-summary"]:
                if form_name in self.storage.data["step_data"]:
                    self.storage.data["step_data"].pop(form_name)

        return self.get_form_step_data(form)

    def get_form(self, step=None, data=None, files=None):
        form = super().get_form(step, data, files)
        # Determine the step if not given
        if step is None:
            step = self.steps.current

        if step == "barrier-export-type":
            location_data = self.storage.get_step_data("barrier-location")
            if location_data:
                default_location = self.get_default_location()

                location_choices = [
                    default_location,
                    (UK_COUNTRY_ID, "United Kingdom"),
                ]
                form.fields["location"].choices = location_choices

        return form

    def get_default_location(self):
        self.countries_options = self.metadata.get_country_list()
        self.trading_blocs = self.metadata.get_trading_bloc_list()
        location_data = self.get_cleaned_data_for_step("barrier-location")

        if location_data:
            default_location_code = location_data.get("location_select", None)
            # Search country list

            default_location_name = next(
                (
                    country["name"]
                    for country in self.countries_options
                    if country["id"] == default_location_code
                ),
                None,
            )
            if default_location_name is None:
                # If country not found search Trading Blocks

                default_location_name = next(
                    (
                        country["name"]
                        for country in self.trading_blocs
                        if country["code"] == str(default_location_code)
                    ),
                    None,
                )

            return (default_location_code, default_location_name)

    def save_report_progress(self):
        # Function to save the current session data for later resume
        # This function is called when clicking "save and exit" button, and when completing
        # each form step.

        # Ensure we have input data to save by checking we have passed at least
        # the first form page some input data
        barrier_title_form = self.get_cleaned_data_for_step("barrier-about")
        if barrier_title_form:
            # Check to see if it is an existing draft barrier/report otherwise create
            barrier_report = self.get_or_create_barrier()
        else:
            # We don't have a barrier title therefore nothing to save
            # Send user to first step
            self.storage.current_step = self.steps.first
            return redirect(self.get_step_url(self.steps.first))

        # Patch the session data to the barrier/report in the DB
        self.client.reports.patch(
            id=barrier_report.id,
            **barrier_title_form,
            new_report_session_data=json.dumps(self.storage.data),
        )

    def done(self, form_list, form_dict, **kwargs):
        submitted_values = {}
        for form in form_list:

            submitted_values[form.prefix] = form.cleaned_data

            # Exclude list for meta fields not required for barrier creation
            exclude_fields = [
                "partially_resolved_date",
                "partially_resolved_description",
                "resolved_date",
                "resolved_description",
                "start_date_unknown",
                "location_select",
                "trading_bloc_EU",
                "trading_bloc_GCC",
                "trading_bloc_EAEU",
                "trading_bloc_Mercosur",
                "companies_affected",
                "unrecognised_company",
                "code",
                "codes",
                "location",
                "countries",
                "trading_blocs",
                "public_information",
            ]
            for name in exclude_fields:
                if name in submitted_values[form.prefix].keys():
                    submitted_values[form.prefix].pop(name)

            # Clean date values
            for name, value in submitted_values[form.prefix].items():
                if isinstance(value, datetime.date):
                    submitted_values[form.prefix][name] = value.isoformat()

        # Check to see if it is an existing draft barrier otherwise create
        barrier_report = self.get_or_create_barrier()

        # Loop through form data, patch barrier with the cleaned data
        if (
            submitted_values["barrier-details-summary"]["details_confirmation"]
            == "completed"
        ):

            public_barrier_form_pages = [
                "barrier-public-title",
                "barrier-public-summary",
            ]

            # Remove forms with no data to commit to the DB
            submitted_values.pop("barrier-details-summary")
            # Information-gate step is on a branch, so may not be present in all situations
            if "barrier-public-information-gate" in submitted_values.keys():
                submitted_values.pop("barrier-public-information-gate")

            for form_submission in submitted_values:
                if form_submission not in public_barrier_form_pages:
                    self.client.reports.patch(
                        id=barrier_report.id, **submitted_values[form_submission]
                    )

            # When report/barrier patched fully, call submit
            self.client.reports.submit(barrier_report.id)

            # After the report is submitted and becomes a barrier, update the public barrier fields
            # This should only trigger if we have completed public-title and public-summary form pages
            if (
                "barrier-public-title" in submitted_values.keys()
                and "barrier-public-summary" in submitted_values.keys()
            ):
                self.client.public_barriers.report_public_barrier_title(
                    id=barrier_report.id,
                    values=submitted_values["barrier-public-title"],
                )
                self.client.public_barriers.report_public_barrier_summary(
                    id=barrier_report.id,
                    values=submitted_values["barrier-public-summary"],
                )

        else:
            # Save progress to the draft barrier in the database
            self.client.reports.patch(
                id=barrier_report.id,
                new_report_session_data=json.dumps(self.storage.data),
                **submitted_values,
            )

        return HttpResponseRedirect(
            reverse(
                "barriers:barrier_detail_from_complete",
                kwargs={"barrier_id": barrier_report.id},
            )
        )

    def get_or_create_barrier(self) -> Barrier:
        """
        Gets or creates a new barrier based on the presence of the barrier_id in self.storage.meta
        """
        if barrier_id := self.storage.data.get("meta", {}).get("barrier_id", None):
            barrier = self.client.reports.get(barrier_id)
        else:
            barrier = self.client.reports.create()
            self.storage.data["meta"] = {"barrier_id": str(barrier.id)}

        return barrier
