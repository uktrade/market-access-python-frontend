from __future__ import annotations

from typing import TYPE_CHECKING

from django import forms

from utils.metadata import MetadataMixin

if TYPE_CHECKING:
    from reports.models import Report


class NewReportBaseForm(MetadataMixin, forms.Form):
    @staticmethod
    def get_barrier_initial(self, barrier: Report) -> dict[str, any]:
        # Akin to a ModelForm include the business logic for
        # generation of initial data inside the form
        raise NotImplementedError()

    def serialize_data(self):
        # Override this method if data needs to be serialized
        # before it can be passed to the Barrier API
        return self.cleaned_data
