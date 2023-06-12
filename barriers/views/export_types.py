from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import FormView, View

from barriers.forms.export_types import EditExportTypesForm, AddExportTypesForm
from utils.metadata import MetadataMixin

from .mixins import BarrierMixin

EXPORT_TYPES = (
    ("goods", "Goods"),
    ("services", "Services"),
    ("investment", "Investment"),
)


class BarrierEditExportType(MetadataMixin, BarrierMixin, FormView):
    template_name = "barriers/edit/export_type.html"
    form_class = EditExportTypesForm
    use_session_export_types = False

    def get(self, request, *args, **kwargs):
        if not self.use_session_export_types:
            request.session["export_types"] = self.barrier.export_types

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        export_types = self.request.session.get("export_types", [])

        context_data.update(
            {
                "export_types": export_types,
            }
        )
        return context_data

    def get_initial(self):
        return {
            "export_types": self.request.session.get("export_types"),
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
        kwargs["export_types"] = [
            (key, value)
            for key, value in EXPORT_TYPES
            if key not in self.barrier.export_types
        ]
        kwargs["barrier_id"] = str(self.kwargs.get("barrier_id"))
        kwargs["token"] = self.request.session.get("sso_token")
        return kwargs


class BarrierEditExportTypeSession(BarrierEditExportType):
    use_session_export_types = True


class BarrierAddExportTypes(MetadataMixin, BarrierMixin, FormView):
    template_name = "barriers/edit/add_export_types.html"
    form_class = AddExportTypesForm

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        export_types = self.request.session.get("export_types", [])
        context_data["export_types"] = export_types
        return context_data

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        export_type_choices = [
            (key, value)
            for key, value in EXPORT_TYPES
            if key not in self.request.session.get("export_types", [])
        ]
        kwargs["export_types"] = export_type_choices
        return kwargs

    def form_valid(self, form):
        export_types = self.request.session.get("export_types", [])
        export_types.append(form.cleaned_data["export_type"])
        self.request.session.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "barriers:edit_export_types_session",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )


class BarrierRemoveExportType(View):
    def post(self, request, *args, **kwargs):
        export_types = self.request.session["export_types"]
        export_type = request.POST.get("export_type")

        export_types.remove(export_type)
        self.request.session["export_types"] = export_types

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse(
            "barriers:edit_export_types_session",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )
