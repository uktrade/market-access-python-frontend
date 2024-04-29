import logging
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs

import dateutil.parser
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.views.generic import FormView

from barriers.forms.notes import AddPublicBarrierNoteForm, EditPublicBarrierNoteForm
from barriers.forms.public_barriers import (
    ApprovePublicBarrierForm,
    PublicBarrierSearchForm,
    PublicEligibilityForm,
    PublishPublicBarrierForm,
    PublishSummaryForm,
    PublishTitleForm,
    UnpublishPublicBarrierForm,
)
from users.mixins import UserMixin
from utils.api.client import MarketAccessAPIClient
from utils.helpers import remove_empty_values_from_dict
from utils.metadata import MetadataMixin

from .mixins import APIBarrierFormViewMixin, BarrierMixin, PublicBarrierMixin
from .search import SearchFormView

logger = logging.getLogger(__name__)


class PublicBarrierListView(MetadataMixin, SearchFormView):
    template_name = "barriers/public_barriers/list.html"
    form_class = PublicBarrierSearchForm
    initial_values = {"status": ["20", "30"]}

    def get_params(self):
        multi_choices_fields = [
            "country",
            "status",
            "sector",
            "region",
            "status",
            "organisation",
            "awaiting_review_from",
        ]
        params = parse_qs(self.request.META.get("QUERY_STRING"), keep_blank_values=True)

        def _is_list_param(field_name):
            return isinstance(params.get(field_name), list)

        def _has_initial_value(field_name):
            return field_name in self.initial_values.keys()

        for multi_choice_field in multi_choices_fields:
            if not params.get(multi_choice_field) and _has_initial_value(
                multi_choice_field
            ):
                params[multi_choice_field] = self.initial_values[multi_choice_field]

        for multi_choice_field in multi_choices_fields:
            if _is_list_param(multi_choice_field):
                params[multi_choice_field] = ",".join(params[multi_choice_field])

        return remove_empty_values_from_dict(params)

    def get_selected_overseas_region(self):
        region_ids = self.get_params().get("region")
        if region_ids:
            return self.metadata.get_overseas_region_by_id(region_ids[0])
        else:
            return None

    def get_public_barriers(self):
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        return client.public_barriers.list(**self.get_params())

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["barriers"] = self.get_public_barriers()
        data["overseas_regions"] = self.metadata.get_overseas_region_choices()
        data["selected_overseas_region"] = self.get_selected_overseas_region()
        data["page"] = "public-barriers"
        return data


class PublicBarrierDetail(
    MetadataMixin, PublicBarrierMixin, BarrierMixin, UserMixin, FormView
):
    template_name = "barriers/public_barriers/detail.html"

    def get_activity(self):
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        activity_items = client.public_barriers.get_activity(barrier_id=self.barrier.id)
        activity_items = [
            item
            for item in activity_items
            if not (item.field == "public_eligibility_summary" and item.new_value == "")
        ]
        activity_items += self.notes
        activity_items.sort(key=lambda object: object.date, reverse=True)
        return activity_items

    def get_context_data(self, **kwargs):
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        context_data = super().get_context_data(**kwargs)

        # Establish type of user accessing the page and pass to template
        # Users can only be in one of these categories.
        user_groups = client.users.get_current().groups_display
        if "Public barrier approver" in user_groups:
            context_data["user_role"] = "Approver"
        elif "Publisher" in user_groups:
            context_data["user_role"] = "Publisher"
        else:
            context_data["user_role"] = "General user"

        context_data["activity_items"] = self.get_activity()

        # Check the activiy items and find the latest public_view_status activity
        # which updated the value to Awaiting publishing, send the users name to the template
        for item in context_data["activity_items"]:
            if isinstance(item.new_value, dict) and item.new_value.get(
                "public_view_status"
            ):
                if item.new_value["public_view_status"][
                    "name"
                ] == "Awaiting publishing" and not context_data.get("approver_name"):
                    context_data["approver_name"] = item.user["name"]
                if item.new_value["public_view_status"][
                    "name"
                ] == "Published" and not context_data.get("publisher_name"):
                    context_data["publisher_name"] = item.user["name"]
                    context_data["published_date"] = item.date

        # There is a 30 day limit after a barrier is set to 'Allowed' for
        # it to be moved into 'Published'. A countdown is displayed in the frontend
        # status box so we need to obtain that count here.
        if self.public_barrier.set_to_allowed_on:
            published_deadline = dateutil.parser.parse(
                self.public_barrier.set_to_allowed_on
            ) + timedelta(days=30)
            diff = published_deadline - datetime.now(timezone.utc)
            context_data["countdown"] = 0 if diff.days <= 0 else diff.days
        else:
            # Have placeholder countdown value for url matching on HTML
            context_data["countdown"] = 30

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
        context_data = self.get_context_data()
        if action:
            client = MarketAccessAPIClient(self.request.session.get("sso_token"))
            barrier_id = self.kwargs.get("barrier_id")

            if action == "submit-for-approval":
                client.public_barriers.ready_for_approval(id=barrier_id)
                submitted_for_approval_success_message = """
                    <span>The approver is the person who checks the public title and summary, and gets
                    clearances. For example, a Grade 6 or 7 in a regional team or a Market Access Coordinator at Post.
                    Once it has been approved the barrier will be sent to the GOV.UK team for final content
                    checks. It can then be published.</span><br><br>
                    <span>This needs to be done within the next <strong>%d</strong> days.
                    For more details see the barrier information and notes on the Barrier publication tab.</span>
                    """
                messages.add_message(
                    self.request,
                    messages.INFO,
                    mark_safe(
                        (
                            submitted_for_approval_success_message
                            % context_data["countdown"]
                        )
                    ),
                    extra_tags="This barrier is now awaiting approval",
                )
            elif action == "remove-for-approval":
                client.public_barriers.allow_for_publishing_process(id=barrier_id)
                approval_revoked_success_message = """
                    <span>The person who approves this barrier has changed the barrier publication status to:
                    <strong>awaiting approval</strong>.</span><br><br>
                    <span>For more details see the barrier information and notes on the Barrier publication tab</span>
                    """
                messages.add_message(
                    self.request,
                    messages.INFO,
                    mark_safe(approval_revoked_success_message),
                    extra_tags="This barrier is not ready for approval",
                )
            elif action == "remove-for-publishing":
                client.public_barriers.ready_for_approval(id=barrier_id)
                publish_rejection_success_message = """
                    <span>The GOV.UK content team can not publish the barrier until it is approved again. To do this
                    the approver will need to complete their checks and submit the barrier for approval.</span><br><br>
                    <span>For more details see the barrier information and notes the publisher has added on the
                    Barrier publication tab.</span>
                    """
                messages.add_message(
                    self.request,
                    messages.INFO,
                    mark_safe(publish_rejection_success_message),
                    extra_tags="This barrier needs to be approved again",
                )
            elif action == "delete-note":
                note_id = self.request.POST.get("note_id")
                client.public_barrier_notes.delete(id=note_id)
            return HttpResponseRedirect(self.get_success_url())
        else:
            form = self.get_form()
            if form.is_valid():
                return self.form_valid(form)
        return self.render_to_response(context_data)

    def get_success_url(self):
        return reverse(
            "barriers:public_barrier_detail",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )


class EditPublicEligibility(APIBarrierFormViewMixin, FormView):
    template_name = "barriers/public_barriers/eligibility.html"
    form_class = PublicEligibilityForm
    success_message_eligible = """
        <span>But it cannot be approved until a public title and summary are added.</span><br><br>
        <span>It will then be reviewed by the approver who checks the public title and summary, and gets
        clearances. The GOV.UK can then review the content and publish it.
        This needs to be done within the next <strong>%d</strong> days.</span><br><br>
        <span>Add the public title and summary on the Barrier publication tab.</span>
        """
    success_message_not_eligible = """
        <span>To start the approval process to decide if this barrier can be made public on GOV.UK, first
        update the barrier publication status to <strong>allowed</strong> and add the public title and summary.
        </span><br><br><span>It will then be reviewed by the approver who checks the public title and summary,
        and gets clearances. The GOV.UK can then review the content and publish it.</span><br><br>
        <span>For more details see the barrier information the Barrier publication tab.</span>
        """

    def get_initial(self):
        barrier_public_eligibility = self.barrier.public_eligibility

        if barrier_public_eligibility:
            public_eligibility = "yes"
        else:
            public_eligibility = "no"

        initial = {
            "public_eligibility": public_eligibility,
        }
        if public_eligibility == "no":
            initial["not_allowed_summary"] = self.barrier.public_eligibility_summary
        else:
            initial["allowed_summary"] = self.barrier.public_eligibility_summary

        return initial

    def get_success_url(self):
        form = self.get_form()
        if form.data["public_eligibility"] == "yes":
            messages.add_message(
                self.request,
                messages.INFO,
                mark_safe((self.success_message_eligible % self.kwargs["countdown"])),
                extra_tags="The barrier publication status has been set to: allowed",
            )
        else:
            messages.add_message(
                self.request,
                messages.INFO,
                mark_safe(self.success_message_not_eligible),
                extra_tags="The publication status is set to: not allowed",
            )

        return reverse(
            "barriers:public_barrier_detail",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )


class EditPublicTitle(APIBarrierFormViewMixin, PublicBarrierMixin, FormView):
    template_name = "barriers/public_barriers/title.html"
    form_class = PublishTitleForm
    success_message = """
        <span>But the barrier cannot be approved until there is both a public title and summary.
        </span><br><br><span>This needs to be done within the next <strong>%d</strong> days,
        along with a review from the approver, and the GOV.UK publishing team.</span><br><br>
        <span>Add the public title and summary on the Barrier publication tab.</span>
        """

    def get_initial(self):
        return {"title": self.public_barrier.title}

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["internal_title"] = self.barrier.title
        context_data["internal_summary"] = self.barrier.summary
        return context_data

    def get_success_url(self):
        messages.add_message(
            self.request,
            messages.INFO,
            mark_safe((self.success_message % self.kwargs["countdown"])),
            extra_tags="The public title has been added",
        )
        return reverse(
            "barriers:public_barrier_detail",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )


class EditPublicSummary(APIBarrierFormViewMixin, PublicBarrierMixin, FormView):
    template_name = "barriers/public_barriers/summary.html"
    form_class = PublishSummaryForm
    success_message = """
        <span>But the barrier cannot be approved until there is both a public title and summary.
        This needs to be done within the next <strong>%d</strong> days,
        along with a review from the approver, and the GOV.UK publishing team.</span><br><br>
        <span>Add the public title and summary on the Barrier publication tab.</span>
        """

    def get_initial(self):
        return {"summary": self.public_barrier.summary}

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["internal_title"] = self.barrier.title
        context_data["internal_summary"] = self.barrier.summary
        return context_data

    def get_success_url(self):
        messages.add_message(
            self.request,
            messages.INFO,
            mark_safe((self.success_message % self.kwargs["countdown"])),
            extra_tags="The public summary has been added",
        )
        return reverse(
            "barriers:public_barrier_detail",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )


class PublicBarrierApprovalConfirmation(
    APIBarrierFormViewMixin, PublicBarrierMixin, FormView
):
    template_name = "barriers/public_barriers/approval_confirmation.html"
    form_class = ApprovePublicBarrierForm
    success_message = """
        <span>Only a member of the GOV.UK publishing team can complete the content checks. They will
        contact the approver if they need more information or context.</span><br><br>
        <span>This needs to be done within the next <strong>%d</strong> days.
        The barrier can then be published.</span><br><br>
        <span>This will be updated in the barrier publication status on the Barrier publication tab.</span>
        """
    rejection_success_message = """
        <span>To start the approval process to decide if this barrier can be made public on GOV.UK, first
        update the barrier publication status to <strong>allowed</strong> and add the public title
        and summary.</span><br><br>
        <span>It will then be reviewed by the approver who checks the public title and summary, and gets
        clearances. The GOV.UK can then review the content and publish it.</span><br><br>
        <span>For more details see the barrier information the Barrier publication tab.</span>
        """

    def get_success_url(self):
        form = self.get_form()
        if "Send to GOV.UK content team" in form.data["submit_approval"]:
            messages.add_message(
                self.request,
                messages.INFO,
                mark_safe((self.success_message % self.kwargs["countdown"])),
                extra_tags="This barrier has been approved and is now with the GOV.UK content team",
            )
        else:
            messages.add_message(
                self.request,
                messages.INFO,
                mark_safe(self.rejection_success_message),
                extra_tags="The publication status is set to: not allowed",
            )
        return reverse(
            "barriers:public_barrier_detail",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )


class PublicBarrierPublishConfirmation(
    APIBarrierFormViewMixin,
    PublicBarrierMixin,
    FormView,
):
    template_name = "barriers/public_barriers/publish_confirmation.html"
    form_class = PublishPublicBarrierForm
    success_message = """
        <span>You can view the barrier on GOV.UK by visiting
        <a class="govuk-link" href="https://www.check-international-trade-barriers.service.gov.uk/">
        Check international trade barriers</a>.</span><br><br>
        <span>For more details see the barrier information and notes on the Barrier publication tab.</span>
        """

    def get_success_url(self):
        messages.add_message(
            self.request,
            messages.INFO,
            mark_safe(self.success_message),
            extra_tags="This barrier has been published on GOV.UK",
        )
        return reverse(
            "barriers:public_barrier_detail",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )


class PublicBarrierUnpublishConfirmation(
    APIBarrierFormViewMixin, PublicBarrierMixin, FormView
):
    template_name = "barriers/public_barriers/unpublish_confirmation.html"
    form_class = UnpublishPublicBarrierForm
    success_message = """
        <span>It can no longer be viewed on
        <a class="govuk-link" href="https://www.check-international-trade-barriers.service.gov.uk/">
        Check international trade barriers</a>.</span><br><br>
        <span>For more details see the barrier information and notes on the Barrier publication tab.</span>
        """

    def get_success_url(self):
        messages.add_message(
            self.request,
            messages.INFO,
            mark_safe(self.success_message),
            extra_tags="This barrier has been removed from GOV.UK",
        )
        return reverse(
            "barriers:public_barrier_detail",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )
