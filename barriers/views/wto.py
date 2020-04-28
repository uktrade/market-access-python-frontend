from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import FormView, RedirectView

from .documents import AddDocumentAjaxView, DeleteDocumentAjaxView
from .mixins import APIBarrierFormViewMixin, SessionDocumentMixin
from barriers.forms.wto import WTOProfileForm, WTOStatusForm, WTODocumentForm

from utils.metadata import get_metadata


class EditWTOStatus(APIBarrierFormViewMixin, FormView):
    template_name = "barriers/edit/wto/status.html"
    form_class = WTOStatusForm

    def form_valid(self, form):
        form.save()
        if (
            form.cleaned_data.get("wto_has_been_notified") is True or
            form.cleaned_data.get("wto_should_be_notified") is True
        ):
            return HttpResponseRedirect(self.get_continue_url())
        return HttpResponseRedirect(self.get_detail_url())

    def get_continue_url(self):
        return reverse(
            "barriers:edit_wto_profile",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )

    def get_detail_url(self):
        return reverse(
            "barriers:barrier_detail",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )

    def get_initial(self):
        if self.barrier.wto_profile:
            wto_profile = self.barrier.wto_profile
            return {
                "wto_has_been_notified": wto_profile.wto_has_been_notified,
                "wto_should_be_notified": wto_profile.wto_should_be_notified,
            }


class EditWTOProfile(SessionDocumentMixin, APIBarrierFormViewMixin, FormView):
    template_name = "barriers/edit/wto/profile.html"
    form_class = WTOProfileForm

    def get(self, request, *args, **kwargs):
        if self.barrier.wto_profile:
            self.initialise_session_with_document(
                document=self.barrier.wto_profile.committee_notification_document,
                session_key=self.get_committee_notification_document_session_key(),
            )
            self.initialise_session_with_document(
                document=self.barrier.wto_profile.meeting_minutes,
                session_key=self.get_meeting_minutes_session_key(),
            )
        return super().get(request, *args, **kwargs)

    def initialise_session_with_document(self, document, session_key):
        if (session_key not in self.request.session and document):
            self.set_session_document(document, session_key)

    def get_initial(self):
        if self.barrier.wto_profile:
            fields = (
                "committee_notified",
                "committee_notification_link",
                "member_states",
                "committee_raised_in",
                "committee_meeting_minutes",
                "raised_date",
                "case_number",
            )
            return {field: self.barrier.wto_profile.data.get(field) for field in fields}

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["committee_notification_document"] = self.get_session_document(
            session_key=self.get_committee_notification_document_session_key()
        )
        context_data["meeting_minutes"] = self.get_session_document(
            session_key=self.get_meeting_minutes_session_key()
        )
        return context_data

    def get_committee_notification_document_session_key(self):
        barrier_id = self.kwargs.get("barrier_id")
        return f"barrier:{barrier_id}:wto:committee_notification_document"

    def get_meeting_minutes_session_key(self):
        barrier_id = self.kwargs.get("barrier_id")
        return f"barrier:{barrier_id}:wto:meeting_minutes"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["metadata"] = get_metadata()
        kwargs["wto_profile"] = self.barrier.wto_profile
        return kwargs

    def form_valid(self, form):
        self.delete_session_documents([
            self.get_committee_notification_document_session_key(),
            self.get_meeting_minutes_session_key(),
        ])
        return super().form_valid(form)


class AddWTODocument(SessionDocumentMixin, AddDocumentAjaxView):
    """
    Calls the API to add a document then stores the document id in the session
    """

    form_class = WTODocumentForm

    def get_session_key(self):
        if self.request.FILES.get("committee_notification_document"):
            barrier_id = self.kwargs.get("barrier_id")
            return f"barrier:{barrier_id}:wto:committee_notification_document"
        elif self.request.FILES.get("meeting_minutes"):
            barrier_id = self.kwargs.get("barrier_id")
            return f"barrier:{barrier_id}:wto:meeting_minutes"

    def get_delete_url(self, document):
        return reverse(
            "barriers:delete_wto_document",
            kwargs={
                "barrier_id": self.kwargs.get("barrier_id"),
                "document_id": document["id"],
            },
        )


class CancelWTODocuments(SessionDocumentMixin, RedirectView):
    """
    Clears the session and redirects to the barrier detail page
    """

    def get(self, request, *args, **kwargs):
        barrier_id = self.kwargs.get("barrier_id")
        self.delete_session_documents([
            f"barrier:{barrier_id}:wto:committee_notification_document",
            f"barrier:{barrier_id}:wto:meeting_minutes",
        ])
        return super().get(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        return reverse(
            "barriers:barrier_detail",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )


class DeleteWTODocument(DeleteDocumentAjaxView):
    """
    Deletes document from the session then either redirects (non-ajax) or returns (ajax)
    """

    def delete_document_from_session(self):
        barrier_id = str(self.kwargs.get("barrier_id"))
        document_id = str(self.kwargs.get("document_id"))

        for session_key in (
            f"barrier:{barrier_id}:wto:committee_notification_document",
            f"barrier:{barrier_id}:wto:meeting_minutes",
        ):
            if self.request.session.get(session_key, {}).get("id") == document_id:
                self.request.session[session_key] = None

    def get_redirect_url(self, *args, **kwargs):
        return reverse(
            "barriers:edit_wto_profile",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )
