from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from django import forms

from barriers.forms.edit import CausedByTradingBlocForm
from reports.model_forms.base import NewReportBaseForm
from utils.forms import YesNoDontKnowBooleanField

if TYPE_CHECKING:
    from reports.models import Report


class NewReportBarrierLocationForm(NewReportBaseForm):
    location = forms.CharField(
        label="Which location is affected by this issue?",
        error_messages={"required": "Select a location"},
        help_text=(
            "A trading bloc should be selected if the barrier applies to the whole "
            "trading bloc. Select a country if the barrier is a national "
            "implementation of a trading bloc regulation (so only applies to that "
            "country)"
        ),
    )

    def __init__(self, barrier=None, *args, **kwargs):
        forms.Form.__init__(self, *args, **kwargs)
        trading_blocs = self.metadata.get_trading_bloc_list()
        countries = self.metadata.get_country_list()
        self.trading_blocs = trading_blocs

    @staticmethod
    def get_barrier_initial(barrier: Report) -> dict[str, any]:
        if barrier.country:
            return {
                "location": barrier.country.get("id"),
                "country": barrier.country.get("id"),
            }
        if barrier.trading_bloc:
            return {
                "location": barrier.trading_bloc.get("code"),
                "trading_bloc": barrier.trading_bloc.get("code"),
            }
        return {}

    def clean_location(self):
        location = self.cleaned_data["location"]
        trading_bloc_codes = [
            trading_bloc["code"] for trading_bloc in self.trading_blocs
        ]
        if location in trading_bloc_codes:
            self.cleaned_data["country"] = None
            self.cleaned_data["trading_bloc"] = location
        else:
            self.cleaned_data["country"] = location
            self.cleaned_data["trading_bloc"] = ""
        return location


class HasAdminAreas:
    # TODO: perhaps reword "HasAdminAreas" to "AffectsEntireCountry"
    #   as it is rather strange to read this in statements
    YES = "1"
    NO = "2"

    @classmethod
    def choices(cls):
        return (
            (cls.YES, "Yes"),
            (cls.NO, "No - just part of the country"),
        )


class NewReportBarrierLocationHasAdminAreasForm(NewReportBaseForm):
    has_admin_areas = forms.ChoiceField(
        required=False,
        label="Does it affect the entire country?",
        choices=HasAdminAreas.choices(),
        error_messages={"required": "Does it affect the entire country?"},
    )

    @staticmethod
    def get_barrier_initial(barrier: Report) -> dict[str, any]:
        return {
            "has_admin_areas": HasAdminAreas.NO
            if barrier.caused_by_admin_areas
            else HasAdminAreas.YES,
        }

    def clean(self) -> Optional[dict[str, any]]:
        cleaned_data = super().clean()
        if cleaned_data["has_admin_areas"] == HasAdminAreas.YES:
            cleaned_data["caused_by_admin_areas"] = False
        elif cleaned_data["has_admin_areas"] == HasAdminAreas.NO:
            cleaned_data["caused_by_admin_areas"] = True
        return cleaned_data


class NewReportBarrierLocationAddAdminAreasForm(NewReportBaseForm):
    admin_areas = forms.CharField(
        required=False,
        label="Which admin area is affected by the barrier?",
        error_messages={"required": "Select an admin area affected by the barrier"},
    )

    def __init__(self, *args, barrier=None, **kwargs):
        super().__init__(*args, barrier=barrier, **kwargs)
        if (barrier is not None) and (barrier.country):
            admin_area_choices = [
                (admin_area["id"], admin_area["name"])
                for admin_area in self.metadata.get_admin_areas_by_country(
                    barrier.country["id"]
                )
            ]

    def clean_selected_admin_areas(self):
        return self.cleaned_data["selected_admin_areas"].split(",")

    @staticmethod
    def get_barrier_initial(barrier: Report) -> dict[str, any]:
        return {
            "admin_areas": [admin_area["id"] for admin_area in barrier.admin_areas],
        }

    def clean_admin_areas(self):
        caused_by_admin_areas = self.cleaned_data.get("caused_by_admin_areas")
        if caused_by_admin_areas is None:
            caused_by_admin_areas = self.barrier.caused_by_admin_areas

        if not caused_by_admin_areas:
            return []

        if not self.cleaned_data.get("admin_areas"):
            return []

        return [
            admin_area
            for admin_area in self.cleaned_data["admin_areas"].split(",")
            if admin_area.strip()
        ]


class NewReportBarrierLocationAdminAreasForm(NewReportBaseForm):
    """
    This form can be submitted empty.
    The admin_areas.choices is considered admin areas selection which is to be used
    during create_barrier.
    """

    admin_areas = forms.ChoiceField(
        label="Selected admin areas",
        choices=[],
        required=False,
    )

    def __init__(self, admin_areas, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["admin_areas"].choices = admin_areas

    @staticmethod
    def get_barrier_initial(barrier: Report) -> dict[str, any]:
        return {
            "admin_areas": barrier.admin_areas,
        }

    def sanitize_data(self):
        return {
            "admin_areas": self.cleaned_data["admin_areas"].split(","),
        }


class NewReportBarrierTradeDirectionForm(NewReportBaseForm):
    trade_direction = forms.ChoiceField(
        label="Which trade direction does this barrier affect?",
        choices=(),
        widget=forms.RadioSelect,
        error_messages={"required": "Select a trade direction"},
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        trade_direction_choices = self.metadata.get_trade_direction_choices()
        self.fields["trade_direction"].choices = trade_direction_choices

    @staticmethod
    def get_barrier_initial(barrier: Report) -> dict[str, any]:
        if barrier.trade_direction:
            return {
                "trade_direction": barrier.trade_direction["id"],
            }
        return {}


class NewReportCausedByTradingBlocForm(CausedByTradingBlocForm, NewReportBaseForm):
    caused_by_trading_bloc = YesNoDontKnowBooleanField(
        label="",
        required=False,
        error_messages={
            "required": "Indicate if the barrier was caused by the trading bloc"
        },
    )

    @staticmethod
    def get_barrier_initial(barrier: Report) -> dict[str, any]:
        if not barrier.trading_bloc:
            # Existing field in the database treats null as "dontknow"
            caused_by_trading_bloc = "dontknow"
            if barrier.caused_by_trading_bloc is True:
                caused_by_trading_bloc = "yes"
            elif barrier.caused_by_trading_bloc is False:
                caused_by_trading_bloc = "no"
            return {
                "caused_by_trading_bloc": caused_by_trading_bloc,
            }
        return {}


class NewReportBarrierLocationMasterForm(
    NewReportBarrierTradeDirectionForm,
    NewReportBarrierLocationHasAdminAreasForm,
    NewReportCausedByTradingBlocForm,
    NewReportBarrierLocationForm,
):
    pass


class NewReportBarrierLocationMasterWithAdminAreaForm(
    NewReportBarrierLocationAddAdminAreasForm, NewReportBarrierLocationMasterForm
):
    pass


class NewReportBarrierLocationAndAdminAreasForm(
    NewReportBarrierLocationForm,
    NewReportBarrierLocationHasAdminAreasForm,
    NewReportCausedByTradingBlocForm,
    NewReportBaseForm,
):
    admin_areas = forms.CharField()


class NewReportBarrierLocationHybridForm(
    NewReportBarrierLocationForm,
    NewReportBarrierLocationHasAdminAreasForm,
    NewReportCausedByTradingBlocForm,
    NewReportBarrierLocationAddAdminAreasForm,
    NewReportBaseForm,
):
    def __init__(self, barrier=None, *args, **kwargs):
        super().__init__(barrier, *args, **kwargs)
        NewReportBarrierLocationForm.__init__(self, *args, **kwargs)
        NewReportBarrierLocationAddAdminAreasForm.__init__(
            self, barrier=barrier, *args, **kwargs
        )

    def serialize_data(self):
        return {
            **NewReportBarrierLocationForm.serialize_data(self),
            **NewReportCausedByTradingBlocForm.serialize_data(self),
            **NewReportBarrierLocationHasAdminAreasForm.serialize_data(self),
        }

    @staticmethod
    def get_barrier_initial(barrier: Report) -> dict[str, any]:
        return {
            **NewReportBarrierLocationForm.get_barrier_initial(barrier),
            **NewReportBarrierLocationAddAdminAreasForm.get_barrier_initial(barrier),
            **NewReportCausedByTradingBlocForm.get_barrier_initial(barrier),
            **NewReportBarrierLocationHasAdminAreasForm.get_barrier_initial(barrier),
        }

    def clean(self):
        cleaned_data = self.cleaned_data
        location = self.cleaned_data.get("location")
        country_id = None
        if (not location) and self.barrier.country:
            country_id = self.barrier.country["id"]
        else:
            country_id = self.cleaned_data.get("country")

        if not country_id:
            return cleaned_data

        does_country_have_trading_bloc = (
            self.metadata.get_trading_bloc_by_country_id(country_id) is not None
        )

        if not does_country_have_trading_bloc:
            cleaned_data["caused_by_trading_bloc"] = None

        does_country_have_admin_areas = (
            self.metadata.get_admin_areas_by_country(country_id) is not None
        )
        if not does_country_have_admin_areas:
            cleaned_data["admin_areas"] = []
        else:
            if cleaned_data.get("has_admin_areas") is None:
                # append validation error to "has_admin_areas" field
                self.add_error(
                    "has_admin_areas",
                    forms.ValidationError("This field is required"),
                )

            if cleaned_data["has_admin_areas"] == HasAdminAreas.YES:
                cleaned_data["caused_by_admin_areas"] = False
            elif cleaned_data["has_admin_areas"] == HasAdminAreas.NO:
                cleaned_data["caused_by_admin_areas"] = True

        return cleaned_data
