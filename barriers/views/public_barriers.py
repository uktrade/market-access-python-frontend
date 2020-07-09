from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import FormView, TemplateView

from .mixins import APIBarrierFormViewMixin, BarrierMixin, PublicBarrierMixin
from barriers.forms.public_barriers import (
    PublicEligibilityForm,
    PublishSummaryForm,
    PublishTitleForm,
)
from barriers.forms.notes import AddPublicBarrierNoteForm, EditPublicBarrierNoteForm

from utils.api.client import MarketAccessAPIClient


class PublicBarrierDetail(PublicBarrierMixin, BarrierMixin, FormView):
    template_name = "barriers/public_barriers/detail.html"

    def get_activity(self):
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        activity_items = client.public_barriers.get_activity(barrier_id=self.barrier.id)
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
