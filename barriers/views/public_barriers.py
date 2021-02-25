from urllib.parse import parse_qs

from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import FormView

from barriers.forms.notes import AddPublicBarrierNoteForm, EditPublicBarrierNoteForm
from barriers.forms.public_barriers import (
    PublicBarrierSearchForm,
    PublicEligibilityForm,
    PublishSummaryForm,
    PublishTitleForm,
)
from utils.api.client import MarketAccessAPIClient
from utils.helpers import remove_empty_values_from_dict
from utils.metadata import MetadataMixin

from .mixins import APIBarrierFormViewMixin, BarrierMixin, PublicBarrierMixin
from .search import SearchFormView


class PublicBarrierListView(MetadataMixin, SearchFormView):
    template_name = "barriers/public_barriers/list.html"
    form_class = PublicBarrierSearchForm
    initial_values = {"status": ["20", "30"]}

    def get_params(self):
        multi_choices_fields = [
            "country",
            "status",
            "sector",
            "region",
            "status",
            "organisation",
        ]
        params = parse_qs(self.request.META.get("QUERY_STRING"), keep_blank_values=True)

        def _is_list_param(field_name):
            return isinstance(params.get(field_name), list)

        def _has_initial_value(field_name):
            return field_name in self.initial_values.keys()

        for multi_choice_field in multi_choices_fields:
            if not params.get(multi_choice_field) and _has_initial_value(
                multi_choice_field
            ):
                params[multi_choice_field] = self.initial_values[multi_choice_field]

        for multi_choice_field in multi_choices_fields:
            if _is_list_param(multi_choice_field):
                params[multi_choice_field] = ",".join(params[multi_choice_field])

        return remove_empty_values_from_dict(params)

    def get_selected_overseas_region(self):
        region_ids = self.get_params().get("region")
        if region_ids:
            return self.metadata.get_overseas_region_by_id(region_ids[0])
        else:
            return None

    def get_public_barriers(self):
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        return client.public_barriers.list(**self.get_params())

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["barriers"] = self.get_public_barriers()
        data["overseas_regions"] = self.metadata.get_overseas_region_choices()
        data["selected_overseas_region"] = self.get_selected_overseas_region()
        data["page"] = "public-barriers"
        return data


class PublicBarrierDetail(PublicBarrierMixin, BarrierMixin, FormView):
    template_name = "barriers/public_barriers/detail.html"

    def get_activity(self):
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        activity_items = client.public_barriers.get_activity(barrier_id=self.barrier.id)
        activity_items = [
            item
            for item in activity_items
            if not (item.field == "public_eligibility_summary" and item.new_value == "")
        ]
        activity_items += self.notes
        activity_items.sort(key=lambda object: object.date, reverse=True)
        return activity_items

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["activity_items"] = self.get_activity()
        context_data["add_note"] = self.request.GET.get("add-note")
        context_data["edit_note"] = self.request.GET.get("edit-note")
        context_data["delete_note"] = self.request.GET.get("delete-note")
        return context_data

    def get_form_class(self):
        if self.request.GET.get("edit-note"):
            return EditPublicBarrierNoteForm
        return AddPublicBarrierNoteForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["token"] = self.request.session.get("sso_token")

        if self.request.GET.get("edit-note"):
            kwargs["note_id"] = int(self.request.GET.get("edit-note"))
        else:
            kwargs["barrier_id"] = self.barrier.id
        return kwargs

    def get_initial(self):
        if self.request.GET.get("edit-note"):
            return {"note": self.note.text}

    def get_note(self):
        note_id = int(self.request.GET.get("edit-note"))

        for note in self.notes:
            if note.id == note_id:
                return note

    def get_notes(self):
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        return client.public_barriers.get_notes(self.barrier.id)

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        action = self.request.POST.get("action")

        if action:
            client = MarketAccessAPIClient(self.request.session.get("sso_token"))
            barrier_id = self.kwargs.get("barrier_id")

            if action == "mark-as-ready":
                client.public_barriers.mark_as_ready(id=barrier_id)
            elif action == "publish":
                client.public_barriers.publish(id=barrier_id)
            elif action == "mark-as-in-progress":
                client.public_barriers.mark_as_in_progress(id=barrier_id)
            elif action == "unpublish":
                client.public_barriers.unpublish(id=barrier_id)
            elif action == "ignore-changes":
                client.public_barriers.ignore_all_changes(id=barrier_id)
            elif action == "delete-note":
                note_id = self.request.POST.get("note_id")
                client.public_barrier_notes.delete(id=note_id)
            return HttpResponseRedirect(self.get_success_url())
        else:
            form = self.get_form()
            if form.is_valid():
                return self.form_valid(form)
        return self.render_to_response(self.get_context_data())

    def get_success_url(self):
        return reverse(
            "barriers:public_barrier_detail",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )


class EditPublicEligibility(APIBarrierFormViewMixin, FormView):
    template_name = "barriers/public_barriers/eligibility.html"
    form_class = PublicEligibilityForm

    def get_initial(self):
        initial = {"public_eligibility": self.barrier.public_eligibility}
        if self.barrier.public_eligibility is True:
            initial["allowed_summary"] = self.barrier.public_eligibility_summary
        elif self.barrier.public_eligibility is False:
            initial["not_allowed_summary"] = self.barrier.public_eligibility_summary
        return initial

    def get_success_url(self):
        return reverse(
            "barriers:public_barrier_detail",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )


class EditPublicTitle(APIBarrierFormViewMixin, PublicBarrierMixin, FormView):
    template_name = "barriers/public_barriers/title.html"
    form_class = PublishTitleForm

    def get_initial(self):
        return {"title": self.public_barrier.title}

    def get_success_url(self):
        return reverse(
            "barriers:public_barrier_detail",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )


class EditPublicSummary(APIBarrierFormViewMixin, PublicBarrierMixin, FormView):
    template_name = "barriers/public_barriers/summary.html"
    form_class = PublishSummaryForm

    def get_initial(self):
        return {"summary": self.public_barrier.summary}

    def get_success_url(self):
        return reverse(
            "barriers:public_barrier_detail",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )
