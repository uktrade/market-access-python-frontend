from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import FormView, View

from .mixins import BarrierContextMixin
from barriers.forms.location import (
    AddAdminAreaForm,
    EditCountryForm,
    EditLocationForm,
)
from utils.metadata import get_metadata


class BarrierEditLocation(BarrierContextMixin, FormView):
    template_name = "barriers/edit/location.html"
    form_class = EditLocationForm
    use_session_location = False

    def get(self, request, *args, **kwargs):
        self.barrier = self.get_barrier()

        if not self.use_session_location:
            request.session['location'] = {
                'country': self.barrier.country['id'],
                'admin_areas': self.barrier.admin_area_ids,
            }

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        metadata = get_metadata()
        country_id = self.request.session['location']['country']
        admin_area_ids = self.request.session['location'].get('admin_areas')
        if admin_area_ids is None:
            admin_area_ids = []

        context_data.update({
            'country': {
                'id': country_id,
                'name': metadata.get_country(country_id)['name'],
            },
            'admin_areas': metadata.get_admin_areas(admin_area_ids)
        })
        return context_data

    def get_initial(self):
        return self.request.session.get('location', {})

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        self.barrier = self.get_barrier()
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse(
            'barriers:barrier_detail',
            kwargs={'barrier_id': self.kwargs.get('barrier_id')}
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        metadata = get_metadata()
        countries = metadata.get_country_list()
        country_choices = [
            (country['id'], country['name'])
            for country in countries
        ]
        kwargs['countries'] = country_choices

        selected_country_id = self.request.session['location']['country']
        admin_areas = metadata.get_admin_areas_by_country(selected_country_id)
        admin_area_choices = [
            (admin_area['id'], admin_area['name'])
            for admin_area in admin_areas
        ]
        kwargs['admin_areas'] = admin_area_choices

        kwargs['barrier_id'] = self.kwargs.get('barrier_id')
        kwargs['token'] = self.request.session.get('sso_token')
        return kwargs


class BarrierEditLocationSession(BarrierEditLocation):
    use_session_location = True


class BarrierEditCountry(BarrierContextMixin, FormView):
    template_name = "barriers/edit/country.html"
    form_class = EditCountryForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        metadata = get_metadata()
        countries = metadata.get_country_list()
        country_choices = [
            (country['id'], country['name'])
            for country in countries
        ]
        kwargs['countries'] = country_choices
        return kwargs

    def get_initial(self):
        return {
            'country': self.request.session['location']['country']
        }

    def form_valid(self, form):
        if (
            self.request.session['location']['country']
            != form.cleaned_data['country']
        ):
            self.request.session['location'] = {
                'country': form.cleaned_data['country'],
                'admin_areas': []
            }
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'barriers:edit_location_session',
            kwargs={'barrier_id': self.kwargs.get('barrier_id')}
        )


class AddAdminArea(BarrierContextMixin, FormView):
    template_name = "barriers/edit/add_admin_area.html"
    form_class = AddAdminAreaForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        metadata = get_metadata()

        selected_country_id = self.request.session['location']['country']
        admin_areas = metadata.get_admin_areas_by_country(selected_country_id)
        admin_area_choices = [
            (admin_area['id'], admin_area['name'])
            for admin_area in admin_areas
            if admin_area['id'] not in
            self.request.session['location'].get('admin_areas', [])
        ]
        kwargs['admin_areas'] = admin_area_choices
        return kwargs

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        metadata = get_metadata()
        admin_area_ids = self.request.session['location'].get(
            'admin_areas', []
        )
        context_data.update({
            'admin_areas': metadata.get_admin_areas(admin_area_ids)
        })
        return context_data

    def form_valid(self, form):
        location = self.request.session['location']
        location['admin_areas'].append(form.cleaned_data['admin_area'])
        self.request.session['location'] = location
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'barriers:edit_location_session',
            kwargs={'barrier_id': self.kwargs.get('barrier_id')}
        )


class RemoveAdminArea(View):
    def post(self, request, *args, **kwargs):
        location = self.request.session['location']
        admin_area = request.POST['admin_area']
        location['admin_areas'].remove(admin_area)
        self.request.session['location'] = location
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse(
            'barriers:edit_location_session',
            kwargs={'barrier_id': self.kwargs.get('barrier_id')}
        )
