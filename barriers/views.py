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


class BarrierDetail(TemplateView):
    template_name = "barriers/barrier_detail.html"

    def get_context_data(self, **kwargs):
        client = MarketAccessAPIClient()
        uuid = self.kwargs.get('id')
        barrier = client.barriers.get(id=uuid)

        notes = client.interactions.list(barrier_id=uuid)
        history = client.barriers.get_history(barrier_id=uuid)
        interactions = notes + history

        if barrier.has_assessment:
            interactions += client.barriers.get_assessment_history(
                barrier_id=uuid
            )

        interactions.sort(key=lambda object: object.date, reverse=True)

        return {
            'barrier': barrier,
            'interactions': interactions,
        }


class APIFormMixin:
    def get(self, request, *args, **kwargs):
        client = MarketAccessAPIClient()
        id = self.kwargs.get('id')
        self.object = client.barriers.get(id=id)
        return super().get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['id'] = self.kwargs.get('id')
        if hasattr(self, 'object'):
            kwargs['instance'] = self.object
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
    def get_success_url(self):
        return reverse(
            'barriers:barrier_detail',
            kwargs={'id': self.kwargs.get('id')}
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


class BarrierAddNote(TemplateView):
    pass


class BarrierEditNote(TemplateView):
    pass


class BarrierDeleteNote(TemplateView):
    pass
