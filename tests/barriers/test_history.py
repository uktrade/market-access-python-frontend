from core.tests import MarketAccessTestCase

from barriers.models import HistoryItem


class BarrierHistoryItemTestCase(MarketAccessTestCase):
    def test_archived(self):
        item = HistoryItem(
            {
                "date": "2020-03-19T15:10:06.110815Z",
                "model": "barrier",
                "field": "archived",
                "old_value": {"archived": False, "unarchived_reason": None},
                "new_value": {
                    "archived": True,
                    "archived_reason": "NOT_A_BARRIER",
                    "archived_explanation": "It's not a barrier",
                },
                "user": {"id": 48, "name": "Test-user"},
                "field_info": {
                    "archived_reason": "NOT_A_BARRIER",
                    "archived_explanation": "It's not a barrier",
                },
            }
        )
        assert item.field_name == "Archived"
        assert item.old_value == {"archived": False, "unarchived_reason": None}
        assert item.new_value == {
            "archived": True,
            "archived_reason": "Not a barrier",
            "archived_explanation": "It's not a barrier",
        }

    def test_categories(self):
        item = HistoryItem(
            {
                "date": "2020-03-24T15:49:19.803670Z",
                "model": "barrier",
                "field": "categories",
                "old_value": ["109", "141"],
                "new_value": ["123"],
                "user": {"id": 48, "name": "Test-user"},
            }
        )
        assert item.field_name == "Barrier categories"
        assert item.old_value == [
            "Locally produced material in goods",
            "Tariffs or import duties",
        ]
        assert item.new_value == ["Limitations on access to key infrastructure"]

    def test_commercial_value(self):
        item = HistoryItem(
            {
                "date": "2020-03-19T09:35:38.130738Z",
                "model": "barrier",
                "field": "commercial_value",
                "old_value": None,
                "new_value": 12345,
                "user": {"id": 48, "name": "Test-user"},
            }
        )
        assert item.field_name == "Commercial value"
        assert item.old_value is None
        assert item.new_value == 12345

    def test_companies(self):
        item = HistoryItem(
            {
                "date": "2020-03-18T16:29:32.415998Z",
                "model": "barrier",
                "field": "companies",
                "old_value": [
                    {
                        "id": "a73efeba-8499-11e6-ae22-56b6b6499611",
                        "name": "Mercury Ltd",
                    }
                ],
                "new_value": [],
                "user": {"id": 48, "name": "Test-user"},
            }
        )
        assert item.field_name == "Companies"
        assert item.old_value == ["Mercury Ltd"]
        assert item.new_value == []

    def test_summary(self):
        item = HistoryItem(
            {
                "date": "2019-08-15T09:54:05.222000Z",
                "model": "barrier",
                "field": "summary",
                "old_value": "Old summary",
                "new_value": "New summary",
                "user": {"id": 48, "name": "Test-user"},
            }
        )
        assert item.field_name == "Summary"
        assert item.old_value == "Old summary"
        assert item.new_value == "New summary"

    def test_location(self):
        item = HistoryItem(
            {
                "date": "2020-03-18T16:31:43.711765Z",
                "model": "barrier",
                "field": "location",
                "old_value": "Angola",
                "new_value": "British Columbia, Alberta (Canada)",
                "user": {"id": 48, "name": "Test-user"},
            }
        )
        assert item.field_name == "Location"
        assert item.old_value == "Angola"
        assert item.new_value == "British Columbia, Alberta (Canada)"

    def test_priority(self):
        item = HistoryItem(
            {
                "date": "2019-10-28T11:47:13.451000Z",
                "model": "barrier",
                "field": "priority",
                "old_value": {
                    "priority": "LOW",
                    "priority_summary": "",
                },
                "new_value": {
                    "priority": "MEDIUM",
                    "priority_summary": "Summary",
                },
                "user": {"id": 48, "name": "Test-user"},
            }
        )
        assert item.field_name == "Priority"
        assert item.old_value == {
            "priority": {"code": "LOW", "name": "Low", "order": 3},
            "priority_summary": "",
        }
        assert item.new_value == {
            "priority": {"code": "MEDIUM", "name": "Medium", "order": 2},
            "priority_summary": "Summary",
        }

    def test_product(self):
        item = HistoryItem(
            {
                "date": "2019-08-15T09:53:02.531000Z",
                "model": "barrier",
                "field": "product",
                "old_value": None,
                "new_value": "Product Name",
                "user": {"id": 48, "name": "Test-user"},
            }
        )
        assert item.field_name == "Product, service or investment affected"
        assert item.old_value is None
        assert item.new_value == "Product Name"

    def test_term(self):
        item = HistoryItem(
            {
                "date": "2020-03-19T15:03:03.599763Z",
                "model": "barrier",
                "field": "term",
                "old_value": 1,
                "new_value": 2,
                "user": {"id": 48, "name": "Test-user"},
            }
        )
        assert item.field_name == "Type"
        assert item.old_value == "A procedural, short-term barrier"
        assert item.new_value == "A long-term strategic barrier"

    def test_sectors(self):
        item = HistoryItem(
            {
                "date": "2019-10-28T11:36:55.767000Z",
                "model": "barrier",
                "field": "sectors",
                "old_value": {
                    "all_sectors": False,
                    "sectors": [],
                },
                "new_value": {
                    "all_sectors": False,
                    "sectors": ["9838cecc-5f95-e211-a939-e4115bead28a"],
                },
                "user": {"id": 48, "name": "Test-user"},
            }
        )
        assert item.field_name == "Sectors affected"
        assert item.old_value["sectors"] == []
        assert item.new_value["sectors"] == ["Automotive"]

    def test_source(self):
        item = HistoryItem(
            {
                "date": "2019-08-15T09:53:02.531000Z",
                "model": "barrier",
                "field": "source",
                "old_value": {
                    "source": "OTHER",
                    "other_source": "Horse",
                },
                "new_value": {
                    "source": "TRADE",
                    "other_source": None,
                },
                "user": {"id": 48, "name": "Test-user"},
            }
        )
        assert item.field_name == "Information source"
        assert item.old_value == "Other - Horse"
        assert item.new_value == "Trade association"

    def test_status(self):
        item = HistoryItem(
            {
                "date": "2019-10-28T11:47:51.875000Z",
                "model": "barrier",
                "field": "status",
                "old_value": {
                    "status": "7",
                    "status_date": "2019-10-28T11:47:51.875000Z",
                    "status_summary": "Summary",
                    "sub_status": None,
                    "sub_status_other": None,
                },
                "new_value": {
                    "status": "1",
                    "status_date": "2019-10-28",
                    "status_summary": "It's pending action.",
                    "sub_status": "UK_GOVT",
                    "sub_status_other": None,
                },
                "user": {"id": 48, "name": "Test-user"},
            }
        )
        assert item.field_name == "Status"
        assert item.old_value["status_text"] == "Unknown"
        assert item.new_value["status_text"] == "Open: Pending action (UK government)"

    def test_tags(self):
        item = HistoryItem(
            {
                "date": "2019-08-15T09:53:02.531000Z",
                "model": "barrier",
                "field": "tags",
                "old_value": [1],
                "new_value": [1, 2],
                "user": {"id": 48, "name": "Test-user"},
            }
        )
        assert item.field_name == "Barrier tags"
        assert item.old_value == ["COVID-19"]
        assert item.new_value == ["COVID-19", "Brexit"]

    def test_title(self):
        item = HistoryItem(
            {
                "date": "2020-03-24T15:01:23.778824Z",
                "model": "barrier",
                "field": "title",
                "old_value": "Old Title",
                "new_value": "New Title",
                "user": {"id": 48, "name": "Test-user"},
            }
        )
        assert item.field_name == "Title"
        assert item.old_value == "Old Title"
        assert item.new_value == "New Title"


class NoteHistoryItemTestCase(MarketAccessTestCase):
    def test_text(self):
        item = HistoryItem(
            {
                "date": "2019-10-28T11:50:00.816000Z",
                "model": "note",
                "field": "text",
                "old_value": "Attach rotary blades to sports cars.",
                "new_value": "Attach rotary cutters to our cars.",
                "user": {"id": 48, "name": "Test-user"},
            }
        )
        assert item.field_name == "Notes"
        assert item.old_value == "Attach rotary blades to sports cars."
        assert item.new_value == "Attach rotary cutters to our cars."
        assert item.diff == (
            '<span class="diff__eq">Attach rotary </span>'
            '<del class="diff__del">blades to sports</del>'
            '<ins class="diff__ins">cutters to our</ins>'
            '<span class="diff__eq"> cars.</span>'
        )

    def test_documents(self):
        item = HistoryItem(
            {
                "date": "2020-03-20T09:42:29.265590Z",
                "model": "note",
                "field": "documents",
                "old_value": [
                    {"id": "e8a4587c-7bf2-48e3-b22b-90276f26e569", "name": "old.jpeg"},
                    {"id": "65b93415-5ddc-4dd0-928f-a758f19c8f15", "name": "same.jpeg"},
                ],
                "new_value": [
                    {"id": "65b93415-5ddc-4dd0-928f-a758f19c8f15", "name": "same.jpeg"},
                    {"id": "958a7fd9-8bf7-4a1f-b222-46d3e69af35a", "name": "new.jpeg"},
                ],
                "user": {"id": 48, "name": "Test-user"},
            }
        )
        assert item.field_name == "Documents"
        assert item.deleted_documents == [
            {"id": "e8a4587c-7bf2-48e3-b22b-90276f26e569", "name": "old.jpeg"}
        ]
        assert item.unchanged_documents == [
            {"id": "65b93415-5ddc-4dd0-928f-a758f19c8f15", "name": "same.jpeg"}
        ]
        assert item.added_documents == [
            {"id": "958a7fd9-8bf7-4a1f-b222-46d3e69af35a", "name": "new.jpeg"}
        ]


class AssessmentHistoryItemTestCase(MarketAccessTestCase):
    def test_documents(self):
        item = HistoryItem(
            {
                "date": "2020-03-20T09:42:29.265590Z",
                "model": "economic_assessment",
                "field": "documents",
                "old_value": [
                    {"id": "e8a4587c-7bf2-48e3-b22b-90276f26e569", "name": "old.jpeg"},
                    {"id": "65b93415-5ddc-4dd0-928f-a758f19c8f15", "name": "same.jpeg"},
                ],
                "new_value": [
                    {"id": "65b93415-5ddc-4dd0-928f-a758f19c8f15", "name": "same.jpeg"},
                    {"id": "958a7fd9-8bf7-4a1f-b222-46d3e69af35a", "name": "new.jpeg"},
                ],
                "user": {"id": 48, "name": "Test-user"},
            }
        )
        assert item.field_name == "Economic assessment: Supporting documents"
        assert item.deleted_documents == [
            {"id": "e8a4587c-7bf2-48e3-b22b-90276f26e569", "name": "old.jpeg"}
        ]
        assert item.unchanged_documents == [
            {"id": "65b93415-5ddc-4dd0-928f-a758f19c8f15", "name": "same.jpeg"}
        ]
        assert item.added_documents == [
            {"id": "958a7fd9-8bf7-4a1f-b222-46d3e69af35a", "name": "new.jpeg"}
        ]

    def test_explanation(self):
        item = HistoryItem(
            {
                "date": "2020-03-19T09:26:02.623635Z",
                "model": "economic_assessment",
                "field": "explanation",
                "old_value": "Old explanation",
                "new_value": "Change to the explanation",
                "user": {"id": 48, "name": "Test-user"},
            }
        )
        assert item.field_name == "Economic assessment: Explanation"
        assert item.old_value == "Old explanation"
        assert item.new_value == "Change to the explanation"

    def test_rating(self):
        item = HistoryItem(
            {
                "date": "2020-03-19T09:26:02.623635Z",
                "model": "economic_assessment",
                "field": "rating",
                "old_value": {
                    "code": "MEDIUMHIGH",
                    "name": "Medium High",
                },
                "new_value": {
                    "code": "LOW",
                    "name": "Low",
                },
                "user": {"id": 48, "name": "Test-user"},
            }
        )
        assert item.field_name == "Economic assessment: Rating"
        assert item.old_value == "Medium High"
        assert item.new_value == "Low"

    def test_import_market_size(self):
        item = HistoryItem(
            {
                "date": "2019-10-29T15:54:05.384000Z",
                "model": "economic_assessment",
                "field": "import_market_size",
                "old_value": 25,
                "new_value": 26,
                "user": {"id": 48, "name": "Test-user"},
            }
        )
        assert item.field_name == "Import market size"
        assert item.old_value == 25
        assert item.new_value == 26

    def test_value_to_economy(self):
        item = HistoryItem(
            {
                "date": "2020-03-19T09:04:12.292070Z",
                "model": "economic_assessment",
                "field": "value_to_economy",
                "old_value": 20000000,
                "new_value": 2000000,
                "user": {"id": 48, "name": "Test-user"},
            }
        )
        assert item.field_name == "Value to UK economy"
        assert item.old_value == 20000000
        assert item.new_value == 2000000

    def test_export_value(self):
        item = HistoryItem(
            {
                "date": "2020-03-19T09:18:16.687291Z",
                "model": "economic_assessment",
                "field": "export_value",
                "old_value": None,
                "new_value": 55000,
                "user": {"id": 48, "name": "Test-user"},
            }
        )
        assert item.field_name == "UK export value"
        assert item.old_value is None
        assert item.new_value == 55000
