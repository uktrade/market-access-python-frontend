from django.urls import reverse
from django.views.generic import FormView, TemplateView

from .forms import (
    UpdateBarrierTitleForm,
    UpdateBarrierProductForm,
    UpdateBarrierDescriptionForm,
    UpdateBarrierSourceForm,
    UpdateBarrierPriorityForm,
    UpdateBarrierEUExitRelatedForm,
    UpdateBarrierProblemStatusForm,
    UpdateBarrierStatusForm,
    UpdateBarrierSectorsForm,
    AddNoteForm,
    EditNoteForm,
)
from utils.api_client import MarketAccessAPIClient


class Dashboard(TemplateView):
    template_name = "barriers/dashboard.html"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data.update({
            'page': 'dashboard',
        })
        return context_data


class AddABarrier(TemplateView):
    template_name = "barriers/add_a_barrier.html"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data.update({
            'page': 'add-a-barrier',
        })
        return context_data


class FindABarrier(TemplateView):
    template_name = "barriers/find_a_barrier.html"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        client = MarketAccessAPIClient()
        barriers = client.barriers.list(
            ordering="-reported_on",
            limit=100,
            offset=0
        )

        context_data.update({
            'barriers': barriers,
            'page': 'find-a-barrier',
        })
        return context_data


class BarrierContextMixin:
    def get(self, request, *args, **kwargs):
        self.barrier = self.get_barrier()
        self.interactions = self.get_interactions()
        return super().get(request, *args, **kwargs)

    def get_barrier(self):
        client = MarketAccessAPIClient()
        barrier_id = self.kwargs.get('barrier_id')
        return client.barriers.get(id=barrier_id)

    def get_interactions(self):
        client = MarketAccessAPIClient()
        barrier_id = self.kwargs.get('barrier_id')
        notes = client.interactions.list(barrier_id=barrier_id)
        history = client.barriers.get_history(barrier_id=barrier_id)
        interactions = notes + history

        if self.barrier.has_assessment:
            interactions += client.barriers.get_assessment_history(
                barrier_id=barrier_id
            )

        interactions.sort(key=lambda object: object.date, reverse=True)

        return interactions

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data.update({
            'barrier': self.barrier,
            'interactions': self.interactions,
        })
        return context_data


class BarrierDetail(BarrierContextMixin, TemplateView):
    template_name = "barriers/barrier_detail.html"


class APIFormMixin:
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def get_initial(self):
        if hasattr(self, 'object'):
            return self.object.to_dict()
        return {}

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(self.kwargs)
        return kwargs

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        if self.object:
            context_data['object'] = self.object
        return context_data


class APIBarrierFormMixin(APIFormMixin):
    def get_object(self):
        client = MarketAccessAPIClient()
        barrier_id = self.kwargs.get('barrier_id')
        return client.barriers.get(id=barrier_id)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['id'] = kwargs.pop('barrier_id')
        return kwargs

    def get_success_url(self):
        return reverse(
            'barriers:barrier_detail',
            kwargs={'barrier_id': self.kwargs.get('barrier_id')}
        )


class BarrierEditTitle(APIBarrierFormMixin, FormView):
    template_name = "barriers/edit/title.html"
    form_class = UpdateBarrierTitleForm


class BarrierEditProduct(APIBarrierFormMixin, FormView):
    template_name = "barriers/edit/product.html"
    form_class = UpdateBarrierProductForm


class BarrierEditDescription(APIBarrierFormMixin, FormView):
    template_name = "barriers/edit/description.html"
    form_class = UpdateBarrierDescriptionForm


class BarrierEditSource(APIBarrierFormMixin, FormView):
    template_name = "barriers/edit/source.html"
    form_class = UpdateBarrierSourceForm


class BarrierEditPriority(APIBarrierFormMixin, FormView):
    template_name = "barriers/edit/priority.html"
    form_class = UpdateBarrierPriorityForm


class BarrierEditEUExitRelated(APIBarrierFormMixin, FormView):
    template_name = "barriers/edit/eu_exit_related.html"
    form_class = UpdateBarrierEUExitRelatedForm


class BarrierEditProblemStatus(APIBarrierFormMixin, FormView):
    template_name = "barriers/edit/problem_status.html"
    form_class = UpdateBarrierProblemStatusForm


class BarrierEditStatus(APIBarrierFormMixin, FormView):
    template_name = "barriers/edit/status.html"
    form_class = UpdateBarrierStatusForm


class BarrierEditSectors(APIBarrierFormMixin, FormView):
    template_name = "barriers/edit/sectors.html"
    form_class = UpdateBarrierSectorsForm


class BarrierAddNote(BarrierContextMixin, APIBarrierFormMixin, FormView):
    template_name = "barriers/edit/add_note.html"
    form_class = AddNoteForm


class BarrierEditNote(BarrierContextMixin, APIFormMixin, FormView):
    template_name = "barriers/barrier_detail.html"
    form_class = EditNoteForm

    def get_object(self):
        note_id = self.kwargs.get('note_id')

        for interaction in self.interactions:
            if interaction.id == note_id:
                return interaction

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
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
