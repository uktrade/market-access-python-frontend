from __future__ import annotations

from typing import TYPE_CHECKING

from django import forms

from reports.model_forms.base import NewReportBaseForm

if TYPE_CHECKING:
    from reports.models import Report


class AreSecorsAffectedKnown:
    YES = "1"
    NO = "0"

    @classmethod
    def choices(cls):
        return (
            (cls.YES, "Yes"),
            (cls.NO, "No, I don't know at the moment"),
        )


class NewReportBarrierHasSectorsForm(NewReportBaseForm):
    sectors_affected = forms.ChoiceField(
        label="Do you know the sector or sectors affected by the barrier?",
        choices=AreSecorsAffectedKnown.choices(),
        error_messages={
            "required": "Select yes or no"
        },
    )

    @staticmethod
    def get_barrier_initial(barrier: Report) -> dict[str, any]:
        sectors_affected = barrier.sectors_affected
        if sectors_affected is None:
            return {}
        if sectors_affected is True:
            return {"sectors_affected": AreSecorsAffectedKnown.YES}
        if sectors_affected is False:
            return {"sectors_affected": AreSecorsAffectedKnown.NO}
        return {}

    def clean_sectors_affected(self):
        sectors_affected = self.cleaned_data["sectors_affected"]
        if sectors_affected == AreSecorsAffectedKnown.NO:
            return False
        elif sectors_affected == AreSecorsAffectedKnown.YES:
            return True
        raise forms.ValidationError("Please select a valid value")

    def serialize_data(self):
        return {"sectors_affected": self.cleaned_data["sectors_affected"]}


class NewReportBarrierSectorsForm(NewReportBaseForm):
    sectors = forms.CharField(label="Selected sectors", required=False)

    def __init__(self, barrier=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not barrier:
            barrier_sectors = [
                sector["id"] for sector in self.metadata.get_sector_list()
            ]
        else:
            barrier_sectors = [sector["id"] for sector in barrier.sectors]
        sectors = (
            (sector["id"], sector["name"])
            for sector in self.metadata.get_sector_list(level=0)
            if sector["id"] in barrier_sectors
        )
        self.fields["sectors"].choices = list(sectors)

    @staticmethod
    def get_barrier_initial(barrier: Report) -> dict[str, any]:
        if barrier.all_sectors is True:
            return {"sectors": ["all"]}
        return {
            "sectors": [sector["id"] for sector in barrier.sectors],
        }

    def clean_sectors(self):
        sectors = self.cleaned_data["sectors"]
        if not sectors:
            raise forms.ValidationError("Select one or more sectors")
        sectors = sectors.split(",")
        if "all" in sectors:
            return ["all"]
        return sectors

    def serialize_data(self):
        if "all" in self.cleaned_data["sectors"]:
            return {"sectors": [], "all_sectors": True}
        return {"sectors": self.cleaned_data["sectors"], "all_sectors": False}


class NewReportBarrierAddSectorsForm(NewReportBaseForm):
    sectors = forms.ChoiceField(
        label="Which sector is affected by the barrier?",
        choices=(),
        error_messages={"required": "Select a sector"},
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        sectors = (
            (sector["id"], sector["name"])
            for sector in self.metadata.get_sector_list(level=0)
        )
        self.fields["sectors"].choices = sectors

    def serialize_data(self):
        return {
            "sectors": self.cleaned_data["sectors"].split(","),
        }

    @staticmethod
    def get_barrier_initial(barrier: Report) -> dict[str, any]:
        return {}
