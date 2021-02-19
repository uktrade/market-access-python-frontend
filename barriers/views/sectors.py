from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import FormView, View

from barriers.forms.sectors import AddSectorsForm, EditSectorsForm
from utils.metadata import MetadataMixin

from .mixins import BarrierMixin


class BarrierEditSectors(MetadataMixin, BarrierMixin, FormView):
    template_name = "barriers/edit/sectors.html"
    form_class = EditSectorsForm
    use_session_sectors = False

    def get(self, request, *args, **kwargs):
        if not self.use_session_sectors:
            request.session["sectors"] = self.barrier.sector_ids
            request.session["all_sectors"] = self.barrier.all_sectors

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        sector_ids = self.request.session.get("sectors", [])

        context_data.update(
            {
                "sectors": self.metadata.get_sectors_by_ids(sector_ids),
                "all_sectors": self.request.session.get("all_sectors"),
            }
        )
        return context_data

    def get_initial(self):
        return {
            "sectors": self.request.session.get("sectors"),
            "all_sectors": self.request.session.get("all_sectors"),
        }

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "barriers:barrier_detail",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["sectors"] = [
            (sector["id"], sector["name"])
            for sector in self.metadata.get_sector_list(level=0)
        ]
        kwargs["barrier_id"] = str(self.kwargs.get("barrier_id"))
        kwargs["token"] = self.request.session.get("sso_token")
        return kwargs


class BarrierEditSectorsSession(BarrierEditSectors):
    use_session_sectors = True


class BarrierAddSectors(MetadataMixin, BarrierMixin, FormView):
    template_name = "barriers/edit/add_sectors.html"
    form_class = AddSectorsForm

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        sector_ids = self.request.session.get("sectors", [])
        context_data["sectors"] = self.metadata.get_sectors_by_ids(sector_ids)
        return context_data

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["sectors"] = [
            (sector["id"], sector["name"])
            for sector in self.metadata.get_sector_list(level=0)
            if sector["id"] not in self.request.session.get("sectors", [])
        ]
        return kwargs

    def form_valid(self, form):
        self.request.session["sectors"].append(form.cleaned_data["sector"])
        self.request.session["all_sectors"] = False
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "barriers:edit_sectors_session",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )


class BarrierRemoveSector(View):
    def post(self, request, *args, **kwargs):
        sectors = self.request.session["sectors"]
        sector = request.POST.get("sector")

        if not sector:
            self.request.session["all_sectors"] = False
        else:
            sectors.remove(sector)
            self.request.session["sectors"] = sectors

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse(
            "barriers:edit_sectors_session",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )


class BarrierAddAllSectors(View):
    def get(self, request, *args, **kwargs):
        self.request.session["sectors"] = []
        self.request.session["all_sectors"] = True
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse(
            "barriers:edit_sectors_session",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )
