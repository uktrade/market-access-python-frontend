from django.http import HttpResponseRedirect
from django.urls import reverse

from reports.constants import FormSessionKeys
from reports.forms.new_report_barrier_location import (
    NewReportBarrierLocationAndAdminAreasForm,
    NewReportBarrierLocationForm,
)
from reports.views import ReportsFormView
from utils.react import form_fields_to_dict


class NewReportBarrierLocationMasterView(ReportsFormView):
    heading_text = "Location of barrier"
    heading_caption = "Question 3 of 7"
    template_name = "reports/new_report_barrier_location_master.html"
    form_class = NewReportBarrierLocationForm
    form_session_key = FormSessionKeys.LOCATION
    success_path = "reports:barrier_location"
    _public_view = False

    @property
    def country_id(self):
        form_data = self.form_group.location_form
        return form_data.get("country")

    @property
    def has_country_id_changed(self):
        country_id = self.form_group.location_form.get("country")
        submitted_country_id = self.request.POST.get("location")
        if not submitted_country_id:
            return False
        return country_id != submitted_country_id

    @property
    def selected_admin_areas(self):
        """
        Returns selected admin areas if any as a GENERATOR.
        :return: TUPLE, (BOOL|has selected admin areas, GENERATOR|selected admin areas)
        """
        area_ids = self.form_group.location_form.get("selected_admin_area", "")
        choices = (
            (area["id"], area["name"])
            for area in self.metadata.get_admin_areas(area_ids)
        )
        return (area_ids != ""), choices

    def get_initial(self):
        """
        Returns the initial data to use for forms on this view.
        """
        initial = super().get_initial()
        self.form_group.refresh_context()
        form_data = self.form_group.get(self.form_session_key, {})
        form_data["location"] = form_data.get("country") or form_data.get(
            "trading_bloc"
        )
        form_data["has_admin_areas"] = form_data.get("has_admin_areas")
        form_data["admin_areas"] = form_data.get("admin_areas")
        form_data["caused_by_trading_bloc"] = form_data.get("caused_by_trading_bloc")

        initial.update(form_data)

        return initial

    def get_form_class(self):
        return NewReportBarrierLocationAndAdminAreasForm

    def form_valid(self, form):

        if hasattr(form, "get_api_params"):
            data = form.get_api_params()
        else:
            data = form.cleaned_data

        self.form_group.set(self.form_session_key, data)
        self.form_group.save()
        self.success()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        form_class = self.get_form_class()
        if form_class != NewReportBarrierLocationForm:
            if self.request.method == "POST":
                return reverse(
                    "reports:barrier_location_uuid",
                    kwargs={"barrier_id": str(self.form_group.barrier_id)},
                )
            return reverse(
                "reports:barrier_sectors_uuid",
                kwargs={"barrier_id": str(self.form_group.barrier_id)},
            )
        return reverse(self.success_path)

    def get_template_names(self):
        return "reports/new_report_barrier_location.html"

    def get_react_data(self, context_data):

        form_kwargs = {
            "countries": self.metadata.get_country_list(),
            "trading_blocs": self.metadata.get_trading_bloc_list(),
            "trading_bloc": None,
        }

        if self.request.method == "POST":
            form = NewReportBarrierLocationAndAdminAreasForm(
                data=self.request.POST, **form_kwargs
            )
        else:
            form = NewReportBarrierLocationAndAdminAreasForm(
                data=self.get_initial(), **form_kwargs
            )

        base_data = {
            "barrier_id": self.form_group.barrier_id,
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

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)

        # country
        context_data["countries"] = self.metadata.get_country_list()
        context_data["trading_blocs"] = self.metadata.get_trading_bloc_list()

        # has a country been picked?
        country_id = self.form_group.location_form.get("country")
        context_data["country_id"] = country_id

        context_data["location_form"] = self.form_group.location_form

        context_data["react_data"] = self.get_react_data(context_data)

        if country_id and (not self.has_country_id_changed):
            # Trade direction
            context_data[
                "trade_direction_choices"
            ] = self.metadata.get_trade_direction_choices()

            trading_bloc = self.metadata.get_trading_bloc_by_country_id(country_id)
            context_data["trading_bloc"] = trading_bloc

            has_admin_areas = self.form_group.location_form.get("has_admin_areas")
            admin_areas = self.metadata.get_admin_areas_by_country(self.country_id)

            context_data["is_country_wide_barrier"] = has_admin_areas
            context_data["has_admin_areas"] = len(admin_areas) > 0

            selected_admin_areas = self.form_group.selected_admin_areas
            context_data["selected_admin_areas_session"] = selected_admin_areas
            selected_admin_areas = selected_admin_areas

            context_data["admin_areas"] = (
                (admin_area["id"], admin_area["name"])
                for admin_area in admin_areas
                if admin_area["id"] not in selected_admin_areas
            )
            context_data["selected_admin_areas"] = (
                (admin_area["id"], admin_area["name"])
                for admin_area in admin_areas
                if admin_area["id"] in selected_admin_areas
            )
            context_data["has_selected_admin_areas"] = len(selected_admin_areas) > 0

            return context_data

        return context_data

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        # country
        kwargs["countries"] = self.metadata.get_country_list()
        kwargs["trading_blocs"] = self.metadata.get_trading_bloc_list()

        # has a country been picked?
        country_id = self.form_group.location_form.get("country")

        if country_id and (not self.has_country_id_changed):

            trading_bloc = self.metadata.get_trading_bloc_by_country_id(country_id)
            kwargs["trading_bloc"] = trading_bloc

        return kwargs
