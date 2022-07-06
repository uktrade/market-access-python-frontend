from __future__ import annotations

from typing import TYPE_CHECKING

from django import forms

from reports.model_forms.base import NewReportBaseForm
from utils.forms import MultipleChoiceFieldWithHelpText

if TYPE_CHECKING:
    from reports.models import Report


class SectorsAffected:
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
        choices=SectorsAffected.choices(),
        error_messages={
            "required": "Select if you are aware of a sector affected by the barrier"
        },
    )

    @staticmethod
    def get_barrier_initial(barrier: Report) -> dict[str, any]:
        return {
            "sectors_affected": barrier.sectors_affected,
        }


class NewReportBarrierSectorsForm(NewReportBaseForm):
    sectors = forms.ChoiceField(label="Selected sectors", choices=(), required=False)

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
        self.fields["sectors"].choices = sectors

    @staticmethod
    def get_barrier_initial(barrier: Report) -> dict[str, any]:
        return {
            "sectors": [sector["id"] for sector in barrier.sectors],
        }


class NewReportBarrierAddSectorsForm(NewReportBaseForm):
    sectors = forms.ChoiceField(
        label="Which sector is affected by the barrier?",
        choices=(),
        error_messages={"required": "Select a sector affected by the barrier"},
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
