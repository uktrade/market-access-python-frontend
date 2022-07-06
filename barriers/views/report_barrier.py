from django.urls import reverse
from django.views.generic import TemplateView

from barriers.models.barriers import Barrier
from barriers.views.mixins import BarrierMixin
from reports.models import Report
from reports.views import ReportsTemplateView
from utils.api.client import MarketAccessAPIClient
from utils.exceptions import APIHttpException


def get_report_barrier_answers(barrier: Report):

    check_answers_page_url = reverse(
        "reports:report_barrier_answers", kwargs={"barrier_id": barrier.id}
    )
    # query_string with next = check_answers_page_url
    qs = "?next={}".format(check_answers_page_url)

    hs_commodity_questions = {}
    hs_countries = set()
    for commodity in barrier.commodities:
        country = commodity["country"]["name"]
        if country not in hs_commodity_questions.keys():
            hs_commodity_questions[country] = {
                "name": f"{country} commodity codes",
                "value": "",
            }
        hs_commodity_questions[country][
            "value"
        ] += f"{commodity['commodity']['full_description']}, "

    return [
        {
            "name": "About the barrier",
            "url": reverse(
                "reports:barrier_about_uuid", kwargs={"barrier_id": barrier.id}
            )
            + qs,
            "questions": [
                {
                    "name": "Name of the barrier",
                    "value": barrier.title,
                },
                {
                    "name": "Describe the barrier",
                    "value": barrier.summary,
                },
                {
                    "name": "Does the summary contain OFFICIAL-SENSITIVE information?",
                    "value": barrier.is_summary_sensitive,
                },
                {
                    "name": "What product, service or investment is affected?",
                    "value": barrier.product,
                },
                {
                    "name": "Who told you about the barrier?",
                    "value": barrier.source_display,  # barrier.reported_by,
                },
                {
                    "name": (
                        "Is this issue caused by or related to any of the following?"
                    ),
                    "value": ",\n".join([tag["title"] for tag in barrier.tags]),
                },
            ],
        },
        {
            "name": "Barrier status",
            "url": reverse(
                "reports:barrier_status_uuid", kwargs={"barrier_id": barrier.id}
            )
            + qs,
            "questions": [
                {
                    "name": "What type of barrier is it?",
                    "value": barrier.term.get("name"),  # barrier.barrier_type,
                },
                {
                    "name": "What is the status of the barrier?",
                    "value": barrier.status_display,
                },
                {
                    "name": "Who is due to take action?",
                    "value": barrier.sub_status_display,
                },
            ],
        },
        {
            "name": "Location of the barrier",
            "url": reverse(
                "reports:barrier_location_uuid", kwargs={"barrier_id": barrier.id}
            )
            + qs,
            "questions": [
                {
                    "name": "Which location is affected by this issue?",
                    "value": barrier.location,
                },
                {
                    "name": (
                        "Was this barrier caused by a regulation introduced by the"
                        " EAEU?"
                    ),
                    "value": barrier.data.get("caused_by_trading_bloc", "") or "",
                },
                {
                    "name": "Does it affect the entire country?",
                    "value": barrier.data.get("has_admin_areas", ""),
                },
                {
                    "name": "Which trade direction does this barrier affect?",
                    "value": barrier.trade_direction_display,
                },
            ],
        },
        {
            "name": "Sectors affected by the barrier",
            "url": reverse(
                "reports:barrier_sectors_uuid", kwargs={"barrier_id": barrier.id}
            )
            + qs,
            "questions": [
                {
                    "name": (
                        "Do you know the sector or sectors affected by the barrier?"
                    ),
                    "value": ",\n".join(
                        [sector.get("name") for sector in barrier.sectors]
                    ),
                }
            ],
        },
        {
            "name": "Barrier category",
            "url": reverse(
                "reports:barrier_categories_uuid", kwargs={"barrier_id": barrier.id}
            )
            + qs,
            "questions": [
                {
                    "name": "Define barrier category",
                    "value": ",\n".join(
                        [category.get("title") for category in barrier.categories]
                    ),
                }
            ],
        },
        {
            "name": "Add HS commodity codes",
            "url": reverse(
                "reports:barrier_commodities_uuid", kwargs={"barrier_id": barrier.id}
            )
            + qs,
            "questions": hs_commodity_questions.values(),
        },
    ]


class ReportBarrierAnswersView(TemplateView):
    template_name = "barriers/report_barrier_answers.html"
    _client: MarketAccessAPIClient = None

    @property
    def client(self):
        if not self._client:
            self._client = MarketAccessAPIClient(self.request.session["sso_token"])
        return self._client

    def get_barrier(self, uuid):
        """Once a report is submitted it becomes a barrier"""
        barrier = self.client.barriers.get(uuid)
        return barrier

    def get_draft_barrier(self, uuid):
        try:
            return self.client.reports.get(uuid)
        except APIHttpException as e:
            if e.status_code == 404:
                # Once a report is submitted it becomes a barrier
                # So it can go missing - let's try to find it
                self.get_barrier(uuid)
            else:
                raise

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        barrier_id = kwargs.get("barrier_id")
        barrier = self.get_draft_barrier(barrier_id)
        context_data["barrier"] = barrier
        context_data["report_barrier_answers"] = get_report_barrier_answers(barrier)
        return context_data
