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
from reports.report_barrier_forms import (
    BarrierAboutForm,
    BarrierCompaniesAffectedForm,
    BarrierDetailsSummaryForm,
    BarrierExportTypeForm,
    BarrierLocationForm,
    BarrierSectorsAffectedForm,
    BarrierStatusForm,
    BarrierTradeDirectionForm,
)
from utils.api.client import MarketAccessAPIClient
from utils.metadata import MetadataMixin

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


class ReportBarrierWizardView(MetadataMixin, NamedUrlSessionWizardView, FormPreview):
    form_list = [
        ("barrier-about", BarrierAboutForm),
        ("barrier-status", BarrierStatusForm),
        ("barrier-location", BarrierLocationForm),
        ("barrier-trade-direction", BarrierTradeDirectionForm),
        ("barrier-sectors-affected", BarrierSectorsAffectedForm),
        ("barrier-companies-affected", BarrierCompaniesAffectedForm),
        ("barrier-export-type", BarrierExportTypeForm),
        ("barrier-details-summary", BarrierDetailsSummaryForm),
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
        self.client = MarketAccessAPIClient(self.request.session.get("sso_token"))

        # Handle legacy React app calls
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return self.ajax(request, *args, **kwargs)

        # Is it resuming a draft barrier
        if draft_barrier_id is not None:
            draft_barrier = self.client.reports.get(id=draft_barrier_id)
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
            # Check to see if it is an existing draft barrier otherwise create
            meta_data = self.storage.data.get("step_data").get("meta", None)
            if meta_data:
                barrier_id = meta_data.get("barrier_id", None)
            else:
                barrier_id = None

            if barrier_id:
                # get draft barrier
                barrier_report = self.client.reports.get(barrier_id)
            else:
                barrier_report = self.client.reports.create()

            # We should at least have passed the first step and have a barrier title
            barrier_title_form = self.get_cleaned_data_for_step("barrier-about")
            if barrier_title_form is None:
                # We don't have a barrire title therefore nothing to save
                # Send user to first step
                self.storage.current_step = self.steps.first
                return redirect(self.get_step_url(self.steps.first))

            self.client.reports.patch(
                id=barrier_report.id,
                **barrier_title_form,
                new_report_session_data=json.dumps(self.storage.data),
            )

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

    def ajax(self, request, *args, **kwargs):
        if request.GET.get("code"):
            form_class = CommodityLookupForm
        # elif request.GET.get("codes"):
        #     form_class = MultiCommodityLookupForm
        else:
            return JsonResponse({"status": "error", "message": "Bad request"})

        lookup_form = self.get_commodity_lookup_form(form_class)

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

    def get_commodity_lookup_form(self, form_class=None):
        if form_class is None:
            form_class = CommodityLookupForm

        # if self.barrier.country:
        #     initial = {"location": self.barrier.country["id"]}
        # elif self.barrier.trading_bloc:
        #     initial = {"location": self.barrier.trading_bloc["code"]}
        # default_location = dict((x, y) for x, y in self.get_default_location())

        selected_location = self.get_default_location()
        default_location = {"id": selected_location[0], "name": selected_location[1]}

        initial = {"location": UK_COUNTRY_ID}

        return form_class(
            initial=initial,
            data=self.request.GET.dict() or None,
            token=self.request.session.get("sso_token"),
            locations=[
                default_location,
                {"id": UK_COUNTRY_ID, "name": "United Kingdom"},
            ],
            # locations=({"id": UK_COUNTRY_ID, "name": "United Kingdom"},),
        )

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)

        if self.steps.current == "barrier-sectors-affected":
            sectors = [
                (sector["id"], sector["name"])
                for sector in self.metadata.get_sector_list(level=0)
            ]
            context.update({"sectors_list": sectors})

        if self.steps.current == "barrier-export-type":
            # TODO: Get the comfirmed commodities from cleaned data - may need to add a hidden field
            confirmed_commodities_data = []
            # confirmed_commodities = (
            #     json.dumps(
            #         self.get_cleaned_data_for_step("barrier-export-type")["commodities"]
            #     )
            #     or None
            # )
            # print(
            #     "cleaned_data",
            #     self.get_cleaned_data_for_step("barrier-export-type")["commodities"],
            # )

            # context.update({"confirmed_commodities": confirmed_commodities})
            # context.update(
            #     {
            #         "confirmed_commodities_data": [
            #             self._to_dict(commodity) for commodity in confirmed_commodities
            #         ]
            #     }
            # )

            context.update({"confirmed_commodities_data": []})

        # Put cleaned data into context for the details summary final step
        if self.steps.current == "barrier-details-summary":
            for step in self.storage.data["step_data"]:
                for key, value in self.get_cleaned_data_for_step(step).items():
                    # Some keys will need formatting to be front-end friendly
                    # while they are currently database friendly.
                    if key == "barrier_status":
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
                        # TODO: What format do these come in? Just the raw code or a dict with product name?

                        # If we are given a list of codes, we SHOULD be able to query the API for them
                        # formatting is very weird though, it can't seem to find the given code -
                        # code/codes doesn't even work as a .get() parameter, does the API serializer need
                        # updating too? might be easier to store all entered HS code details into clean/session
                        # data rather than making a whole new lookup
                        # Files to check: barriers/forms/commodities.py and barriers/views/commodities.py
                        logger.critical("******************")
                        logger.critical(value)
                        logger.critical("******************")
                        hs6_codes = []
                        for commodity_code in value:
                            hs6_code = commodity_code[:6].ljust(10, "0")
                            hs6_codes.append(hs6_code)

                        logger.critical("******************")
                        logger.critical(hs6_codes)
                        logger.critical(",".join(hs6_codes))
                        logger.critical("******************")
                        commodities_details = self.client.commodities.list(
                            codes=hs6_codes
                        )
                        logger.critical("******************")
                        logger.critical(commodities_details)
                        logger.critical("******************")

                        # commodity_details_list = self.client.commodities.list(codes=",".join(value))
                        # logger.critical("-----")
                        # logger.critical(commodity_details_list)
                        # logger.critical("-----")
                        # for commodity in commodity_details_list:
                        #    logger.critical("******************")
                        #    logger.critical(commodity.__dict__)
                        #    logger.critical("******************")

                        context[key] = value
                    else:
                        context[key] = value

        return context

    def process_step(self, form):
        return self.get_form_step_data(form)

    def get_form(self, step=None, data=None, files=None):
        form = super().get_form(step, data, files)
        # determine the step if not given
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
        # TODO - use get_step_cleaned_data() here instead
        location_data = self.storage.get_step_data("barrier-location")
        if location_data:
            default_location_code = location_data.get(
                "barrier-location-location_select", None
            )
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

    def done(self, form_list, form_dict, **kwargs):
        submitted_values = {}
        for form in form_list:
            submitted_values = {**submitted_values, **form.cleaned_data}

        # Exclude list for meta fields not required for barrier creation
        exclude_fields = [
            "partially_resolved_date",
            "partially_resolved_description",
            "resolved_date",
            "resolved_description",
            "location_select",
            "trading_bloc_EU",
            "trading_bloc_GCC",
            "trading_bloc_EAEU",
            "trading_bloc_Mercosur",
            "companies_affected",
            "unrecognised_company",
            "code",
            "location",
            "countries",
            "trading_blocs",
        ]

        # Clean date values
        for name, value in submitted_values.items():
            if isinstance(value, datetime.date):
                submitted_values[name] = value.isoformat()

        for name in exclude_fields:
            submitted_values.pop(name)

        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        # Check to see if it is an existing draft barrier otherwise create
        meta_data = self.storage.data.get("step_data").get("meta", None)

        if meta_data:
            barrier_id = meta_data.get("barrier_id", None)
        else:
            barrier_id = None

        if barrier_id:
            # get draft barrier
            barrier_report = self.client.reports.get(barrier_id)

        else:
            barrier_report = self.client.reports.create()

        # submitted_values["id"] = barrier_report.id
        # TODO Need to add this to journey
        # submitted_values["is_draft"] = False

        if submitted_values["details_confirmation"] == "completed":
            submitted_values.pop("details_confirmation")
            # client.reports.patch(
            #    id=barrier_report.id,
            #    **submitted_values,
            # )

            print("creating final barrier")
            # TODO need to use the submit endpiont
            # submitted_values["new_report_session_data"] = None
            # self.client.put(f"reports/{barrier_id}/submit")
            # self.client.reports.submit(self.barrier_id)

            logger.critical("***********************************")
            logger.critical(submitted_values)
            logger.critical("-")
            logger.critical(str(barrier_report.id) + " == " + str(barrier_id))
            # logger.critical("-")
            # logger.critical(form_list)
            logger.critical("***********************************")

            # Submit method pass takes barrier_id, api side uses that ID to get all
            # the data it has on the report and validate it. Kind of redundant if we've
            # validated it at point of entry.
            # client.reports.submit(
            #    **submitted_values,
            # )
            # client.reports.patch(
            #    id=barrier_report.id,
            #    **submitted_values,
            # )

            logger.critical("+++++++++++++++++++++++++++++++++")
            logger.critical("Starting PATCH BATCH(tm)")
            # TIME FOR PATCH BATCH:
            # About form
            self.client.reports.patch(
                id=barrier_report.id,
                title=submitted_values["barrier_title"],
                summary=submitted_values["barrier_description"],
            )
            logger.critical("About form PATCH BATCHED(tm)")

            # Status form
            logger.critical("THE STATUS FORM: ")
            self.client.reports.patch(
                id=barrier_report.id,
                status=submitted_values["barrier_status"],
                status_date=submitted_values["status_date"],
                status_summary=submitted_values["status_summary"],
                # NEW FIELD; START DATE KNOWN is_start_date_known = submitted_values["start_date_known"],
                # NEW FIELD; START DATE start_date = submitted_values["start_date"],
                # NEW FIELD; CURRENTLY ACTIVE is_currently_active = submitted_values["currently_active"],
            )
            logger.critical("Status form PATCH BATCHED(tm)")

            # logger.critical("-")
            # logger.critical(submitted_values["country"])
            # self.client.reports.patch(id=barrier_report.id, country=submitted_values["country"])
            # logger.critical(submitted_values["admin_areas"])
            # self.client.reports.patch(id=barrier_report.id, admin_areas=submitted_values["admin_areas"])
            # logger.critical(submitted_values["caused_by_admin_areas"])
            # self.client.reports.patch(id=barrier_report.id,
            # caused_by_admin_areas=submitted_values["caused_by_admin_areas"])
            # logger.critical(submitted_values["trading_bloc"])
            # self.client.reports.patch(id=barrier_report.id, trading_bloc=submitted_values["trading_bloc"])
            # logger.critical(submitted_values["caused_by_trading_bloc"])
            # self.client.reports.patch(id=barrier_report.id,
            #  caused_by_trading_bloc=submitted_values["caused_by_trading_bloc"])
            # logger.critical("-")
            # Location form
            self.client.reports.patch(
                id=barrier_report.id,
                country=submitted_values["country"],
                admin_areas=submitted_values["admin_areas"],
                caused_by_admin_areas=submitted_values["caused_by_admin_areas"],
                trading_bloc=submitted_values["trading_bloc"],
                caused_by_trading_bloc=submitted_values["caused_by_trading_bloc"],
            )
            logger.critical("Location form PATCH BATCHED(tm)")

            # Trade direction form
            self.client.reports.patch(
                id=barrier_report.id,
                trade_direction=submitted_values["trade_direction"],
            )
            logger.critical("Trade direction form PATCH BATCHED(tm)")

            # Sectors form
            logger.critical("-")
            logger.critical(submitted_values["sectors"])
            self.client.reports.patch(
                id=barrier_report.id,
                # NEW FIELD; MAIN SECTORS =submitted_values["main_sector"],
                sectors=json.loads(submitted_values["sectors"]),
                sectors_affected=True,
            )
            logger.critical("Sectors form PATCH BATCHED(tm)")

            # Companies form
            self.client.reports.patch(
                id=barrier_report.id,
                companies=submitted_values["companies"],
                # COMPANIES NOT IN SERIALISER YET =submitted_values["related_organisations"],
            )
            logger.critical("Companies form PATCH BATCHED(tm)")

            # Commodities and export types form
            self.client.reports.patch(
                id=barrier_report.id,
                # NEW FIELD EXPORT TYPE export_types = submitted_values["export_type"],
                # NEW FIELD EXPORT DESCRIPTION = submitted_values["export_description"],
                commodities=submitted_values["codes"],
            )
            logger.critical("Commodities form PATCH BATCHED(tm)")

            logger.critical("+++++++++++++++++++++++++++++++++")

            self.client.reports.submit(barrier_report.id)

        # TODO MONDAY:
        # add new fields not added by Uka to the api
        # add new fields to the report serialiser

        else:
            self.client.reports.patch(
                # id=barrier_report.id,
                new_report_session_data=json.dumps(self.storage.data),
                **submitted_values,
            )

        # BarrierReportSerializer fields:
        # fields = (
        #    "admin_areas",
        #    "all_sectors",
        #    "caused_by_trading_bloc",
        #    "code",
        #    "country",
        #    "created_by",
        #    "created_on",
        #    "id",
        #    "is_summary_sensitive",
        #    "is_top_priority",
        #    "location",
        #    "modified_by",
        #    "modified_on",
        #    "next_steps_summary",
        #    "other_source",
        #    "product",
        #    "progress",
        #    "sectors",
        #    "sectors_affected",
        #    "source",
        #    "status",
        #    "status_date",
        #    "status_summary",
        #    "sub_status",
        #    "sub_status_other",
        #    "summary",
        #    "tags",
        #    "term",
        #    "title",
        #    "trade_direction",
        #    "trading_bloc",
        #    "categories",
        #    "commodities",
        #    "draft",
        #    "caused_by_admin_areas",
        # )

        # client.reports.patch(
        #     barrier_title="Test barrier",
        #     barrier_description="Description",
        #     barrier_status="2",
        #     partially_resolved_date=None,
        #     partially_resolved_description=None,
        #     resolved_date=None,
        #     resolved_description=None,
        #     start_date_known=False,
        #     start_date="2022-08-01",
        #     currently_active=None,
        #     location_select="TB00016",
        #     # admin_areas=None,
        #     trading_bloc_EU=None,
        #     trading_bloc_GCC=None,
        #     trading_bloc_EAEU=None,
        #     trading_bloc_Mercosur=None,
        #     country=None,
        #     trading_bloc="TB00016",
        #     # trade_direction="EXPORTING",
        #     main_sector="af959812-6095-e211-a939-e4115bead28a",
        #     # sectors=None,
        #     companies_affected=None,
        #     unrecognised_company=None,
        #     # companies=None,
        #     # related_organisations=None,
        #     # export_type=None,
        #     # export_description="eewwe",
        #     # code=None,
        #     # location=None,
        #     # codes=None,
        #     # countries=None,
        #     # trading_blocs=None,
        #     id=barrier_report.id,
        # )
        # Todo Remove once submit and is_draft is handled
        # client.reports.patch(
        #    **submitted_values,
        # )

        return HttpResponseRedirect(reverse("barriers:dashboard"))
