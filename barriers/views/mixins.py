import urllib.parse
from http import HTTPStatus

from django.http import Http404, HttpResponseRedirect
from django.urls import reverse

from utils.api.client import MarketAccessAPIClient
from utils.exceptions import APIHttpException

from barriers.models import PublicBarrier


class BarrierMixin:
    include_interactions = False
    _barrier = None
    _interactions = None
    _notes = None
    _note = None
    _action_plan = None

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

    @property
    def action_plan(self):
        if not self._action_plan:
            self._action_plan = self.get_action_plan()
        return self._action_plan

    def get_barrier(self):
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        barrier_id = self.kwargs.get("barrier_id")
        try:
            return client.barriers.get(id=barrier_id)
        except APIHttpException as e:
            if e.status_code == HTTPStatus.NOT_FOUND:
                raise Http404()
            raise

    def get_interactions(self):
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        activity = client.barriers.get_activity(barrier_id=self.barrier.id)
        interactions = self.notes + activity
        interactions.sort(key=lambda object: object.date, reverse=True)
        return interactions

    def get_notes(self):
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        return client.notes.list(barrier_id=self.barrier.id)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["barrier"] = self.barrier
        if self.include_interactions:
            context_data["interactions"] = self.interactions
        return context_data

    def get_note(self):
        note_id = self.kwargs.get("note_id")

        for note in self.notes:
            if note.id == note_id:
                return note

    def get_action_plan(self):
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        barrier_id = self.kwargs.get("barrier_id")
        return client.action_plans.get_barrier_action_plan(barrier_id=barrier_id)


class PublicBarrierMixin:
    _public_barrier = None

    @property
    def public_barrier(self):
        if not self._public_barrier:
            self._public_barrier = self.get_public_barrier()
        return self._public_barrier

    def get_public_barrier(self) -> PublicBarrier:
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        barrier_id = self.kwargs.get("barrier_id")
        return client.public_barriers.get(id=barrier_id)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["public_barrier"] = self.public_barrier
        return context_data


class TeamMembersContextMixin:
    _team_members = None

    def get_team_members(self):
        if self._team_members is None:
            client = MarketAccessAPIClient(self.request.session.get("sso_token"))
            self._team_members = client.barriers.get_team_members(
                barrier_id=self.kwargs.get("barrier_id")
            )

        return self._team_members

    def get_team_member(self, team_member_id):
        for member in self.get_team_members():
            if member["id"] == team_member_id:
                return member

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["team_members"] = self.get_team_members()
        return context_data


class APIFormViewMixin:
    _object = None

    @property
    def object(self):
        if not self._object:
            self._object = self.get_object()
        return self._object

    def get_form_kwargs(self, **kwargs):
        if self.request.method == "GET":
            kwargs["initial"] = self.get_initial()
        elif self.request.method in ("POST", "PUT"):
            kwargs.update(
                {
                    "data": self.request.POST,
                    "files": self.request.FILES,
                }
            )

        kwargs.update(self.kwargs)
        kwargs["token"] = self.request.session.get("sso_token")
        return kwargs

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["object"] = self.object
        return context_data


class APIBarrierFormViewMixin(BarrierMixin, APIFormViewMixin):
    def get_object(self):
        return self.barrier

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["id"] = str(kwargs.pop("barrier_id"))
        return kwargs

    def get_success_url(self):
        return reverse(
            "barriers:barrier_detail",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )


class SessionDocumentMixin:
    """
    Helper class for handling session documents.

    The session key can be specific to a particular object, so that multiple
    objects can be edited without interfering with eachother.
    """

    def get_session_key(self):
        raise NotImplementedError

    def get_session_document(self, session_key=None):
        if session_key is None:
            session_key = self.get_session_key()
        return self.request.session.get(session_key)

    def get_session_documents(self):
        return self.request.session.get(self.get_session_key(), [])

    def set_session_document(self, document, session_key=None):
        if session_key is None:
            session_key = self.get_session_key()
        self.request.session[session_key] = {
            "id": document.id,
            "name": document.name,
            "size": document.size,
        }

    def set_session_documents(self, documents):
        session_key = self.get_session_key()
        self.request.session[session_key] = [
            {
                "id": document.id,
                "name": document.name,
                "size": document.size,
            }
            for document in documents
        ]

    def delete_session_documents(self, session_keys=()):
        if not session_keys:
            session_keys = [self.get_session_key()]

        for session_key in session_keys:
            try:
                del self.request.session[session_key]
            except KeyError:
                pass


class AnalyticsMixin:
    """
    Redirects a short querystring to the full GA querystring with utm tags.

    See example below to redirect ?en=u to the full GA querystring.
    Each tag value can either be a string or a dictionary lookup.

    utm_tags = {
        "en": {
            "utm_source": "notification-email",
            "utm_medium": "email",
            "utm_campaign": {
                "n": "new-barriers",
                "u": "updated-barriers",
            }
        }
    }
    """

    utm_tags = {}

    def get_utm_querystring(self):
        for key, tag_data in self.utm_tags.items():
            if key in self.request.GET:
                params = {}
                for tag_name, tag_value in tag_data.items():
                    if isinstance(tag_value, dict):
                        value = self.request.GET.get(key)
                        params[tag_name] = tag_value.get(value, "")
                    else:
                        params[tag_name] = tag_value
                return urllib.parse.urlencode(params)

    def dispatch(self, request, *args, **kwargs):
        utm_querystring = self.get_utm_querystring()
        if utm_querystring is not None:
            return HttpResponseRedirect(f"{request.path_info}?{utm_querystring}")
        return super().dispatch(request, *args, **kwargs)


class EconomicAssessmentMixin:
    _economic_assessment = None

    @property
    def economic_assessment(self):
        if self._economic_assessment is None:
            for assessment in self.barrier.economic_assessments:
                if str(assessment.id) == str(self.kwargs.get("assessment_id")):
                    self._economic_assessment = assessment
                    return self._economic_assessment
            raise Http404("Economic assessment does not exist")
        return self._economic_assessment

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        if self.kwargs.get("assessment_id"):
            context_data["economic_assessment"] = self.economic_assessment
        return context_data


class EconomicImpactAssessmentMixin:
    _economic_impact_assessment = None

    @property
    def economic_impact_assessment(self):
        if self._economic_impact_assessment is None:
            for assessment in self.barrier.economic_impact_assessments:
                if str(assessment.id) == str(self.kwargs.get("assessment_id")):
                    self._economic_impact_assessment = assessment
                    return self._economic_impact_assessment
            raise Http404("Valuation assessment does not exist")
        return self._economic_impact_assessment

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        if self.kwargs.get("assessment_id"):
            context_data["economic_impact_assessment"] = self.economic_impact_assessment
        return context_data


class ResolvabilityAssessmentMixin:
    _resolvability_assessment = None

    @property
    def resolvability_assessment(self):
        if self._resolvability_assessment is None:
            for assessment in self.barrier.resolvability_assessments:
                if assessment.id == str(self.kwargs.get("assessment_id")):
                    self._resolvability_assessment = assessment
                    return self._resolvability_assessment
            raise Http404("Resolvability assessment does not exist")
        return self._resolvability_assessment


class StrategicAssessmentMixin:
    _strategic_assessment = None

    @property
    def strategic_assessment(self):
        if self._strategic_assessment is None:
            for assessment in self.barrier.strategic_assessments:
                if assessment.id == str(self.kwargs.get("assessment_id")):
                    self._strategic_assessment = assessment
                    return self._strategic_assessment
            raise Http404("Strategic assessment does not exist")
        return self._strategic_assessment
