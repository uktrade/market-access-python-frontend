from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import FormView, RedirectView, TemplateView

from .mixins import BarrierMixin, SessionDocumentMixin
from .documents import AddDocumentAjaxView, DeleteDocumentAjaxView
from ..forms.notes import AddNoteForm, EditNoteForm, NoteDocumentForm

from utils.api.client import MarketAccessAPIClient


class NoteSessionDocumentMixin(SessionDocumentMixin):
    def get_session_key(self):
        barrier_id = self.kwargs.get("barrier_id")
        note_id = self.kwargs.get("note_id")
        if note_id is None:
            note_id = self.request.GET.get("note_id", "new")
        return f"barrier:{barrier_id}:note:{note_id}:documents"


class BarrierAddNote(NoteSessionDocumentMixin, BarrierMixin, FormView):
    template_name = "barriers/edit/add_note.html"
    form_class = AddNoteForm
    include_interactions = True

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["documents"] = self.get_session_documents()
        return context_data

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["barrier_id"] = self.barrier.id
        kwargs["token"] = self.request.session.get("sso_token")
        return kwargs

    def form_valid(self, form):
        form.save()
        self.delete_session_documents()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "barriers:barrier_detail",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )


class BarrierEditNote(NoteSessionDocumentMixin, BarrierMixin, FormView):
    template_name = "barriers/barrier_detail.html"
    form_class = EditNoteForm
    include_interactions = True

    def get(self, request, *args, **kwargs):
        session_key = self.get_session_key()
        if session_key not in self.request.session:
            self.set_session_documents(self.note.documents)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["documents"] = self.get_session_documents()
        return context_data

    def get_initial(self):
        if self.request.method == "GET":
            return {"note": self.note.text}

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["token"] = self.request.session.get("sso_token")
        kwargs["barrier_id"] = self.kwargs.get("barrier_id")
        kwargs["note_id"] = self.kwargs.get("note_id")
        return kwargs

    def form_valid(self, form):
        form.save()
        self.delete_session_documents()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "barriers:barrier_detail",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )


class AddNoteDocument(NoteSessionDocumentMixin, AddDocumentAjaxView):
    form_class = NoteDocumentForm

    def get_delete_url(self, document):
        return reverse(
            "barriers:delete_note_document",
            kwargs={
                "barrier_id": self.kwargs.get("barrier_id"),
                "document_id": document["id"],
            },
        )


class DeleteNoteDocument(NoteSessionDocumentMixin, DeleteDocumentAjaxView):
    """
    Deletes a document from the session
    """

    def get_redirect_url(self, *args, **kwargs):
        return reverse(
            "barriers:edit_note",
            kwargs={
                "barrier_id": self.kwargs.get("barrier_id"),
                "note_id": self.request.GET.get("note_id"),
            },
        )


class CancelNoteDocument(NoteSessionDocumentMixin, RedirectView):
    """
    Clears the session and redirects to the barrier detail page
    """

    def get(self, request, *args, **kwargs):
        self.delete_session_documents()
        return super().get(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        return reverse(
            "barriers:barrier_detail",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )


class BarrierDeleteNote(NoteSessionDocumentMixin, BarrierMixin, TemplateView):
    template_name = "barriers/delete_note.html"
    include_interactions = True

    def get_template_names(self):
        if self.request.is_ajax():
            return ["barriers/modals/delete_note.html"]
        return ["barriers/delete_note.html"]

    def get_context_data(self, **kwargs):
        if self.request.is_ajax():
            return {
                "barrier": {"id": self.kwargs.get("barrier_id")},
                "note": self.note,
            }

        context_data = super().get_context_data(**kwargs)
        context_data["note"] = self.note
        return context_data

    def post(self, request, *args, **kwargs):
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        client.notes.delete(self.kwargs.get("note_id"))
        self.delete_session_documents()
        url = reverse(
            "barriers:barrier_detail",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )
        return HttpResponseRedirect(url)
