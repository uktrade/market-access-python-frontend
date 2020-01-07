from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import FormView, View

from .mixins import BarrierMixin
from ..forms.types import (
    AddTypeForm,
    EditTypesForm,
)
from utils.metadata import get_metadata


class AddBarrierType(BarrierMixin, FormView):
    template_name = "barriers/types/add_type.html"
    form_class = AddTypeForm

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data.update({
            'barrier_types': self.get_barrier_type_list()
        })
        return context_data

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['barrier_types'] = self.get_barrier_type_list()
        return kwargs

    def get_barrier_type_list(self):
        """
        Get a list of all barrier types excluding any already selected
        """
        metadata = get_metadata()
        selected_barrier_type_ids = [
            str(barrier_type['id'])
            for barrier_type in self.request.session.get('barrier_types', [])
        ]
        return [
            barrier_type
            for barrier_type in metadata.get_barrier_type_list()
            if str(barrier_type['id']) not in selected_barrier_type_ids
        ]

    def form_valid(self, form):
        """
        Add the new barrier type to the session and redirect
        """
        metadata = get_metadata()
        barrier_type = metadata.get_barrier_type(
            form.cleaned_data['barrier_type']
        )
        barrier_types = self.request.session.get('barrier_types', [])
        barrier_types.append({
            'id': barrier_type['id'],
            'title': barrier_type['title'],
        })
        self.request.session['barrier_types'] = barrier_types
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'barriers:edit_types_session',
            kwargs={'barrier_id': self.kwargs.get('barrier_id')}
        )


class BarrierEditTypes(BarrierMixin, FormView):
    template_name = "barriers/types/edit.html"
    form_class = EditTypesForm
    use_session_types = False

    def get(self, request, *args, **kwargs):
        if not self.use_session_types:
            request.session['barrier_types'] = self.barrier.get_barrier_types()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data.update({
            'barrier_types': self.request.session.get('barrier_types', [])
        })
        return context_data

    def get_initial(self):
        barrier_types = self.request.session.get('barrier_types', [])
        return {
            'barrier_types': [type['id'] for type in barrier_types],
        }

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['barrier_id'] = self.kwargs.get('barrier_id')
        kwargs['token'] = self.request.session.get('sso_token')
        kwargs['barrier_types'] = self.request.session.get('barrier_types', [])
        return kwargs

    def form_valid(self, form):
        form.save()
        del self.request.session['barrier_types']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'barriers:barrier_detail',
            kwargs={'barrier_id': self.kwargs.get('barrier_id')}
        )


class BarrierEditTypesSession(BarrierEditTypes):
    use_session_types = True


class BarrierRemoveType(View):
    """
    Remove the barrier type from the session and redirect
    """
    def post(self, request, *args, **kwargs):
        barrier_types = self.request.session.get('barrier_types', [])
        barrier_type_id = request.POST.get('barrier_type_id')

        self.request.session['barrier_types'] = [
            barrier_type for barrier_type in barrier_types
            if barrier_type_id != str(barrier_type['id'])
        ]
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse(
            'barriers:edit_types_session',
            kwargs={'barrier_id': self.kwargs.get('barrier_id')}
        )
