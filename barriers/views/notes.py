from django.urls import reverse
from django.views.generic import FormView, TemplateView

from .mixins import APIBarrierFormMixin, APIFormMixin, BarrierContextMixin
from barriers.forms.notes import AddNoteForm, EditNoteForm


class BarrierAddNote(BarrierContextMixin, APIBarrierFormMixin, FormView):
    template_name = "barriers/edit/add_note.html"
    form_class = AddNoteForm
    include_interactions = True


class BarrierEditNote(BarrierContextMixin, APIFormMixin, FormView):
    template_name = "barriers/barrier_detail.html"
    form_class = EditNoteForm
    include_interactions = True

    def get_object(self):
        note_id = self.kwargs.get('note_id')

        for interaction in self.interactions:
            if interaction.id == note_id:
                return interaction

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['token'] = self.request.session.get('sso_token')
        kwargs['barrier_id'] = self.kwargs.get('barrier_id')
        kwargs['note_id'] = self.kwargs.get('note_id')
        return kwargs

    def get_success_url(self):
        return reverse(
            'barriers:barrier_detail',
            kwargs={'barrier_id': self.kwargs.get('barrier_id')}
        )


class BarrierDeleteNote(TemplateView):
    pass
