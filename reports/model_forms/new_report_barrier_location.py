from __future__ import annotations

from typing import TYPE_CHECKING

from django import forms

from barriers.forms.edit import CausedByTradingBlocForm
from barriers.forms.location import EditCountryOrTradingBlocForm
from reports.model_forms.base import NewReportBaseForm

if TYPE_CHECKING:
    from reports.models import Report


class NewReportBarrierLocationForm(EditCountryOrTradingBlocForm, NewReportBaseForm):
    def __init__(self, *args, **kwargs):
        forms.Form.__init__(self, *args, **kwargs)
        trading_blocs = self.metadata.get_trading_bloc_list()
        countries = self.metadata.get_country_list()
        self.trading_blocs = trading_blocs
        self.fields["location"].choices = (
            (
                "Trading blocs",
                tuple([(bloc["code"], bloc["name"]) for bloc in trading_blocs]),
            ),
            (
                "Countries",
                tuple((country["id"], country["name"]) for country in countries),
            ),
        )

    @staticmethod
    def get_barrier_initial(barrier: Report) -> dict[str, any]:
        if barrier.country:
            return {
                "location": barrier.country.get("id"),
            }
        if barrier.trading_bloc:
            return {
                "location": barrier.trading_bloc.get("code"),
            }
        return {}


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
        label="Does it affect the entire country?",
        choices=HasAdminAreas.choices(),
        error_messages={"required": "Does it affect the entire country?"},
    )

    @staticmethod
    def get_barrier_initial(barrier: Report) -> dict[str, any]:
        return {
            "has_admin_areas": barrier.has_admin_areas,
        }


class NewReportBarrierLocationAddAdminAreasForm(NewReportBaseForm):
    admin_areas = forms.ChoiceField(
        required=False,
        label="Which admin area is affected by the barrier?",
        choices=[],
        error_messages={"required": "Select an admin area affected by the barrier"},
    )
    # selected_admin_areas = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, admin_areas, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["admin_areas"].choices = admin_areas

    def clean_selected_admin_areas(self):
        return self.cleaned_data["selected_admin_areas"].split(",")

    @staticmethod
    def get_barrier_initial(barrier: Report) -> dict[str, any]:
        return {
            "admin_areas": barrier.admin_areas,
        }


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
        return {
            "trade_direction": barrier.trade_direction,
        }


class NewReportCausedByTradingBlocForm(CausedByTradingBlocForm):
    @staticmethod
    def get_barrier_initial(barrier: Report) -> dict[str, any]:
        if barrier.trading_bloc:
            return {
                "caused_by_trading_bloc": barrier.trading_bloc.get("code"),
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


# class NewReportBarrierLocationMasterAddAdminAreaForm(
#     NewReportBarrierLocationAddAdminAreasForm, NewReportBarrierLocationMasterForm
# ):
#     def


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
    def serialize_data(self):
        data = {
            **self.cleaned_data,
            "admin_areas": [
                item for item in self.cleaned_data["admin_areas"].split(",") if item
            ],
        }
        return data

    @staticmethod
    def get_barrier_initial(barrier: Report) -> dict[str, any]:
        return {
            **NewReportBarrierLocationForm.get_barrier_initial(barrier),
            **NewReportBarrierLocationAddAdminAreasForm.get_barrier_initial(barrier),
            **NewReportCausedByTradingBlocForm.get_barrier_initial(barrier),
            **NewReportBarrierLocationHasAdminAreasForm.get_barrier_initial(barrier),
        }
