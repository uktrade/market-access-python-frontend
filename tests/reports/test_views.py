from http import HTTPStatus

from django.urls import resolve, reverse
from mock import patch

from core.tests import MarketAccessTestCase, ReportsTestCase
from reports.models import Report
from reports.views import DeleteReport, DraftBarriers, NewReport, ReportDetail


class NewReportsViewTestCase(MarketAccessTestCase):

    def test_new_report_url_resolves_to_correct_view(self):
        match = resolve('/reports/new/')
        assert match.func.view_class == NewReport

    def test_new_report_view_loads_correct_template(self):
        url = reverse('reports:new_report')
        response = self.client.get(url)
        assert HTTPStatus.OK == response.status_code
        self.assertTemplateUsed(response, "reports/new_report.html")

    def test_new_report_returns_correct_html(self):
        url = reverse('reports:new_report')
        expected_title = '<title>Market Access - Report a barrier</title>'
        expected_callout = '<a href="/reports/new/start/" class="callout__button callout__button--start">Start now</a>'
        task_item = '<li class="task-list__item">'
        expected_tasks_count = 5

        response = self.client.get(url)
        html = response.content.decode('utf8')

        assert HTTPStatus.OK == response.status_code
        assert expected_title in html
        assert expected_callout in html
        tasks_count = html.count(task_item)
        assert expected_tasks_count is tasks_count, f'Expected {expected_tasks_count} tasks, got: {tasks_count}'


class DraftBarriersViewTestCase(ReportsTestCase):

    def setUp(self):
        super().setUp()
        self.url = reverse('reports:draft_barriers')

    def test_draft_barrier_url_resolves_to_correct_view(self):
        match = resolve('/draft-barriers/')
        assert match.func.view_class == DraftBarriers

    @patch("utils.api.client.ReportsResource.list")
    def test_draft_barriers_view_loads_correct_template(self, _mock_list):
        response = self.client.get(self.url)
        assert HTTPStatus.OK == response.status_code
        self.assertTemplateUsed(response, "reports/draft_barriers.html")

    @patch("utils.api.client.ReportsResource.list")
    def test_draft_barriers_returns_correct_html(self, mock_list):
        mock_list.return_value = (Report(self.draft_barrier(4)), Report(self.draft_barrier(5)),)
        expected_title = "<title>Market Access - Draft barriers</title>"
        my_draft_barriers_table = '<table class="standard-table my-draft-barriers">'
        draft_barrier_row = '<tr class="standard-table__row draft-barrier-item">'
        expected_row_count = 2

        response = self.client.get(self.url)
        html = response.content.decode('utf8')

        assert HTTPStatus.OK == response.status_code
        assert expected_title in html
        assert my_draft_barriers_table in html
        row_count = html.count(draft_barrier_row)
        assert expected_row_count == row_count,\
            f'Expected {expected_row_count} least one sector option, got: {row_count}'


class ReportDetailViewTestCase(ReportsTestCase):

    def test_report_detail_url_resolves_to_correct_view(self):
        draft = self.draft_barrier(1)
        match = resolve(f'/reports/{draft["id"]}/')
        assert match.func.view_class == ReportDetail

    @patch("utils.api.client.ReportsResource.get")
    def test_report_detail_view_loads_correct_template(self, mock_get):
        draft = self.draft_barrier(1)
        mock_get.return_value = Report(draft)
        url = reverse('reports:draft_barrier_details_uuid', kwargs={"barrier_id": draft["id"]})

        response = self.client.get(url)

        assert HTTPStatus.OK == response.status_code
        self.assertTemplateUsed(response, "reports/report_detail.html")

    @patch("utils.api.client.ReportsResource.get")
    def test_report_detail_view_loads_html__with_sections_not_started(self, mock_get):
        draft = self.draft_barrier(30)
        url = reverse(
            "reports:draft_barrier_details_uuid",
            kwargs={"barrier_id": draft["id"]}
        )
        mock_get.return_value = Report(draft)
        expected_title = "<title>Market Access - Add - Barrier details</title>"
        expected_callout_container = '<div class="callout callout--warn callout--with-button">'
        expected_callout_heading = '<h2 class="callout__heading">Unfinished barrier for</h2>'
        submit_button = '<input type="submit" value="Submit barrier" class="callout__button">'
        complete_class = "task-list__item__banner--complete"
        expected_complete_class_count = 3

        response = self.client.get(url)
        html = response.content.decode("utf8")

        assert HTTPStatus.OK == response.status_code
        assert expected_title in html
        assert expected_callout_container in html
        assert expected_callout_heading in html
        assert submit_button not in html
        completed_count = html.count(complete_class)
        assert expected_complete_class_count == completed_count,\
            f'Expected {expected_complete_class_count} admin areas, got: {completed_count}'

    @patch("utils.api.client.ReportsResource.get")
    def test_report_detail_view_loads_html__with_all_sections_completed(self, mock_get):
        draft = self.draft_barrier(6)
        url = reverse(
            "reports:draft_barrier_details_uuid",
            kwargs={"barrier_id": draft["id"]}
        )
        mock_get.return_value = Report(draft)
        expected_title = "<title>Market Access - Add - Barrier details</title>"
        expected_callout_container = '<div class="callout callout--success callout--with-button">'
        expected_callout_heading = '<h2 class="callout__heading">All tasks completed for</h2>'
        submit_button = '<input type="submit" value="Submit barrier" class="callout__button">'
        complete_class = "task-list__item__banner--complete"
        expected_complete_class_count = 5

        response = self.client.get(url)
        html = response.content.decode("utf8")

        assert HTTPStatus.OK == response.status_code
        assert expected_title in html
        assert expected_callout_container in html
        assert expected_callout_heading in html
        assert expected_callout_heading in html
        assert submit_button in html
        completed_count = html.count(complete_class)
        assert expected_complete_class_count == completed_count, \
            f'Expected {expected_complete_class_count} admin areas, got: {completed_count}'

    @patch("utils.api.client.ReportsResource.get")
    @patch("reports.helpers.ReportFormGroup.submit")
    def test_submit_report(self, mock_submit, mock_get):
        """
        Users can submit reports that has all steps complete.
        When this happens the user is redirected to the barriers detail page.
        """
        draft = self.draft_barrier(6)
        url = reverse(
            "reports:draft_barrier_details_uuid",
            kwargs={"barrier_id": draft["id"]}
        )
        redirect_url = reverse(
            "barriers:barrier_detail",
            kwargs={"barrier_id": draft["id"]}
        )
        mock_get.return_value = Report(draft)
        mock_submit.return_value = {"status_code": 200}

        response = self.client.post(url, {})

        self.assertRedirects(response, redirect_url)
        assert mock_submit.called is True


class DeleteReportViewTestCase(ReportsTestCase):

    def setUp(self):
        super().setUp()
        self.draft = self.draft_barrier(5)
        self.url = reverse("reports:delete_report", kwargs={"barrier_id": self.draft["id"]})

    def test_delete_report_url_resolves_to_correct_view(self):
        match = resolve(f'/reports/{self.draft["id"]}/delete/')
        assert match.func.view_class == DeleteReport

    @patch("utils.api.client.ReportsResource.list")
    @patch("utils.api.client.ReportsResource.get")
    @patch("utils.api.client.ReportsResource.delete")
    def test_delete_report_view_loads_correct_template(self, mock_delete, mock_get, _mock_list):
        mock_get.return_value = Report(self.draft)
        redirect_url = reverse("reports:draft_barriers")

        response = self.client.post(self.url, {})

        self.assertRedirects(response, redirect_url)
        assert mock_get.called is True
        assert mock_delete.called is True
