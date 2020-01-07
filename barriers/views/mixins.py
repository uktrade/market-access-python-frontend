from django.urls import reverse

from utils.api_client import MarketAccessAPIClient


class BarrierContextMixin:
    include_interactions = False
    _barrier = None
    _interactions = None
    _notes = None
    _note = None

    @property
    def barrier(self):
        if not self._barrier:
            self._barrier = self.get_barrier()
        return self._barrier

    @property
    def interactions(self):
        if not self._interactions:
            self._interactions = self.get_interactions()
        return self._interactions

    @property
    def note(self):
        if not self._note:
            self._note = self.get_note()
        return self._note

    @property
    def notes(self):
        if not self._notes:
            self._notes = self.get_notes()
        return self._notes

    def get_barrier(self):
        client = MarketAccessAPIClient(self.request.session.get('sso_token'))
        barrier_id = self.kwargs.get('barrier_id')
        return client.barriers.get(id=barrier_id)

    def get_interactions(self):
        client = MarketAccessAPIClient(self.request.session.get('sso_token'))
        barrier_id = self.kwargs.get('barrier_id')

        history = client.barriers.get_history(barrier_id=barrier_id)
        interactions = self.notes + history

        if self.barrier.has_assessment:
            interactions += client.barriers.get_assessment_history(
                barrier_id=barrier_id
            )

        interactions.sort(key=lambda object: object.date, reverse=True)

        return interactions

    def get_notes(self):
        client = MarketAccessAPIClient(self.request.session.get('sso_token'))
        barrier_id = self.kwargs.get('barrier_id')
        return client.interactions.list(barrier_id=barrier_id)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['barrier'] = self.barrier
        if self.include_interactions:
            context_data['interactions'] = self.interactions
        return context_data

    def get_note(self):
        note_id = self.kwargs.get('note_id')

        for note in self.notes:
            if note.id == note_id:
                return note


class TeamMembersContextMixin:
    _team_members = None

    def get_team_members(self):
        if self._team_members is None:
            client = MarketAccessAPIClient(
                self.request.session.get('sso_token')
            )
            self._team_members = client.barriers.get_team_members(
                barrier_id=self.kwargs.get('barrier_id')
            ).get('results', [])

        return self._team_members

    def get_team_member(self, team_member_id):
        for member in self.get_team_members():
            if member['id'] == team_member_id:
                return member

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['team_members'] = self.get_team_members()
        return context_data


class AssessmentMixin:
    _assessment = None

    @property
    def assessment(self):
        if not self._assessment:
            if hasattr(self, '_barrier') and not self.barrier.has_assessment:
                return None
            self._assessment = self.get_assessment()
        return self._assessment

    def get_assessment(self):
        client = MarketAccessAPIClient(self.request.session.get('sso_token'))
        barrier_id = self.kwargs.get('barrier_id')
        return client.barriers.get_assessment(barrier_id=barrier_id)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['assessment'] = self.assessment
        return context_data


class APIFormMixin:
    _object = None

    @property
    def object(self):
        if not self._object:
            self._object = self.get_object()
        return self._object

    def get_initial(self):
        if self.request.method.lower() == "get":
            return self.object.to_dict()
        return {}

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(self.kwargs)
        kwargs['token'] = self.request.session.get('sso_token')
        return kwargs

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['object'] = self.object
        return context_data


class APIBarrierFormMixin(APIFormMixin):
    def get_object(self):
        client = MarketAccessAPIClient(self.request.session.get('sso_token'))
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


class SessionDocumentMixin:
    """
    Helper class for handling session documents.

    The session key can be specific to a particular object, so that multiple
    objects can be edited without interfering with eachother.
    """
    def get_session_key(self):
        raise NotImplementedError

    def get_session_documents(self):
        return self.request.session.get(self.get_session_key(), [])

    def set_session_documents(self, documents):
        session_key = self.get_session_key()
        self.request.session[session_key] = [
            {
                'id': document.id,
                'name': document.name,
                'size': document.size,
            }
            for document in documents
        ]

    def delete_session_documents(self):
        try:
            del self.request.session[self.get_session_key()]
        except KeyError:
            pass
