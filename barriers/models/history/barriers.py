import dateutil.parser

from barriers.constants import ARCHIVED_REASON
from barriers.models.commodities import format_commodity_code
from utils.metadata import Statuses

from .base import BaseHistoryItem, GenericHistoryItem
from .utils import PolymorphicBase


class ArchivedHistoryItem(BaseHistoryItem):
    field = "archived"
    field_name = "Archived"
    modifier = "archived"

    def __init__(self, data):
        super().__init__(data)

        if not self.new_value["archived"]:
            self.modifier = "unarchived"

    def get_value(self, value):
        if archived_reason := value.get("archived_reason"):
            value["archived_reason"] = ARCHIVED_REASON[archived_reason]
        return value


class CategoriesHistoryItem(BaseHistoryItem):
    field = "categories"
    field_name = "Barrier categories"

    def get_value(self, value):
        category_names = [
            self.metadata.get_category(category).get("title")
            for category in value or []
        ]
        category_names.sort()
        return category_names


class CausedByTradingBlocHistoryItem(BaseHistoryItem):
    field = "caused_by_trading_bloc"
    field_name = "Caused by trading bloc"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        country_trading_bloc = self.get_country_trading_bloc()
        if country_trading_bloc:
            self.field_name = (
                "Was this barrier caused by a regulation introduced by "
                f"{country_trading_bloc['name']}?"
            )

    def get_country_trading_bloc(self):
        if self.data["old_value"]["country_trading_bloc"]:
            return self.data["old_value"]["country_trading_bloc"]
        elif self.data["new_value"]["country_trading_bloc"]:
            return self.data["new_value"]["country_trading_bloc"]

    def get_value(self, value):
        return value["caused_by_trading_bloc"]


class CommercialValueHistoryItem(BaseHistoryItem):
    field = "commercial_value"
    field_name = "Commercial value estimate"


class CommercialValueExplanationHistoryItem(BaseHistoryItem):
    field = "commercial_value_explanation"
    field_name = "Commercial value explanation"


class CommoditiesHistoryItem(BaseHistoryItem):
    field = "commodities"
    field_name = "Commodities"

    @property
    def diff(self):
        grouped = self.get_values_grouped_by_location()
        diff = {}
        for country_name, item in grouped.items():
            old_codes = set([value["code"] for value in item["old_value"]])
            new_codes = set([value["code"] for value in item["new_value"]])
            added_codes = new_codes.difference(old_codes)
            removed_codes = old_codes.difference(new_codes)
            unchanged_codes = new_codes.intersection(old_codes)
            diff[country_name] = {"removed": [], "unchanged": [], "added": []}
            for value in item.get("old_value"):
                if value["code"] in removed_codes:
                    diff[country_name]["removed"].append(value)
            for value in item.get("new_value"):
                if value["code"] in added_codes:
                    diff[country_name]["added"].append(value)
                if value["code"] in unchanged_codes:
                    diff[country_name]["unchanged"].append(value)

        return diff

    def get_location_name(self, value):
        if value.get("country"):
            return value["country"]["name"]
        elif value.get("trading_bloc"):
            return value["trading_bloc"]["name"]

    def get_values_grouped_by_location(self):
        grouped = {}

        for value in self.old_value:
            key = self.get_location_name(value)
            grouped.setdefault(key, {"old_value": [], "new_value": []})
            grouped[key]["old_value"].append(value)

        for value in self.new_value:
            key = self.get_location_name(value)
            grouped.setdefault(key, {"old_value": [], "new_value": []})
            grouped[key]["new_value"].append(value)

        return grouped

    def get_value(self, value):
        for item in value:
            item["code_display"] = format_commodity_code(item["code"])
        return value


class CompaniesHistoryItem(BaseHistoryItem):
    field = "companies"
    field_name = "Companies"

    def get_value(self, value):
        return [company["name"] for company in value or []]


class EconomicAssessmentEligibilityHistoryItem(BaseHistoryItem):
    field = "economic_assessment_eligibility"
    field_name = "Economic assessment: Eligibility"

    def get_value(self, value):
        if value is True:
            return "Eligible"
        elif value is False:
            return "Ineligible"


class EconomicAssessmentEligibilitySummaryHistoryItem(BaseHistoryItem):
    field = "economic_assessment_eligibility_summary"
    field_name = "Economic assessment: Eligibility summary"


class EstimatedResolutionDateHistoryItem(BaseHistoryItem):
    field = "estimated_resolution_date"
    field_name = "Estimated resolution date"

    def get_value(self, value):
        if value:
            return dateutil.parser.parse(value)


class IsSummarySensitiveHistoryItem(BaseHistoryItem):
    field = "is_summary_sensitive"
    field_name = "Summary status"


class LocationHistoryItem(BaseHistoryItem):
    field = "location"
    field_name = "Location"


class OrganisationHistoryItem(BaseHistoryItem):
    field = "organisations"
    field_name = "Organisations"

    def get_value(self, value):
        organisations = [
            self.metadata.get_government_organisation(org) for org in value or {}
        ]
        names = [t["name"] for t in organisations]
        return names


class PolicyTeamsHistoryItem(BaseHistoryItem):
    field = "policy_teams"
    field_name = "Policy teams"

    def get_value(self, value):
        policy_teams_names = [
            self.metadata.get_policy_team(policy_team).get("title")
            for policy_team in value or []
        ]
        policy_teams_names.sort()
        return policy_teams_names


class PriorityHistoryItem(BaseHistoryItem):
    field = "priority"
    field_name = "Priority"
    modifier = "priority"

    def get_value(self, value):
        value["priority"] = self.metadata.get_priority(value["priority"])
        return value


class ProductHistoryItem(BaseHistoryItem):
    field = "product"
    field_name = "Product, service or investment affected"


class PublicEligibilitySummaryHistoryItem(BaseHistoryItem):
    field = "public_eligibility_summary"
    field_name = "Publish status summary"
    modifier = "note"


class SectorsHistoryItem(BaseHistoryItem):
    field = "sectors"
    field_name = "Sectors affected"

    def get_value(self, value):
        return {
            "all_sectors": value["all_sectors"],
            "sectors": [
                self.metadata.get_sector(sector_id).get("name", "Unknown")
                for sector_id in value["sectors"] or []
            ],
        }


class SourceHistoryItem(BaseHistoryItem):
    field = "source"
    field_name = "Information source"

    def get_value(self, value):
        source = self.metadata.get_source(value["source"])
        if value["other_source"]:
            return f"{source} - {value['other_source']}"
        return source


class StatusHistoryItem(BaseHistoryItem):
    field = "status"
    field_name = "Status"
    modifier = "status"

    def get_value(self, value):
        if value["status_date"]:
            value["status_date"] = dateutil.parser.parse(value["status_date"])
        value["status_short_text"] = self.metadata.get_status_text(value["status"])
        value["status_text"] = self.metadata.get_status_text(
            status_id=value["status"],
            sub_status=value["sub_status"],
            sub_status_other=value["sub_status_other"],
        )
        value["is_resolved"] = value["status"] in (
            Statuses.RESOLVED_IN_PART,
            Statuses.RESOLVED_IN_FULL,
        )
        value["show_summary"] = value["status"] in (
            Statuses.OPEN_IN_PROGRESS,
            Statuses.UNKNOWN,
        )
        return value


class SummaryHistoryItem(BaseHistoryItem):
    field = "summary"
    field_name = "Summary"

    def get_value(self, value):
        return value or ""


class TagsHistoryItem(BaseHistoryItem):
    field = "tags"
    field_name = "Barrier tags"

    def get_value(self, value):
        tags = [self.metadata.get_barrier_tag(tag) for tag in value or {}]
        sorted_tags = sorted(tags, key=lambda k: k["order"])
        tag_names = [t["title"] for t in sorted_tags]
        return tag_names


class TermHistoryItem(BaseHistoryItem):
    field = "term"
    field_name = "Type"

    def get_value(self, value):
        return self.metadata.get_term(value)


class TitleHistoryItem(BaseHistoryItem):
    field = "title"
    field_name = "Title"


class TradeCategoryHistoryItem(BaseHistoryItem):
    field = "trade_category"
    field_name = "Trade category"

    def get_value(self, value):
        if value:
            return value.get("name")


class TradeDirectionHistoryItem(BaseHistoryItem):
    field = "trade_direction"
    field_name = "Trade direction"

    def get_value(self, value):
        return self.metadata.get_trade_direction(str(value))


class TopPriorityStatusHistoryItem(BaseHistoryItem):
    field = "top_priority_status"
    field_name = "PB100 Priority Status"

    def get_value(self, value):
        if value["value"]:
            return value


class BarrierHistoryItem(PolymorphicBase):
    """
    Polymorphic wrapper for HistoryItem classes
    """

    model = "barrier"
    key = "field"
    subclasses = (
        ArchivedHistoryItem,
        CategoriesHistoryItem,
        CausedByTradingBlocHistoryItem,
        CommercialValueHistoryItem,
        CommercialValueExplanationHistoryItem,
        CommoditiesHistoryItem,
        CompaniesHistoryItem,
        EconomicAssessmentEligibilityHistoryItem,
        EconomicAssessmentEligibilitySummaryHistoryItem,
        EstimatedResolutionDateHistoryItem,
        IsSummarySensitiveHistoryItem,
        LocationHistoryItem,
        OrganisationHistoryItem,
        PolicyTeamsHistoryItem,
        ProductHistoryItem,
        PriorityHistoryItem,
        PublicEligibilitySummaryHistoryItem,
        SectorsHistoryItem,
        SourceHistoryItem,
        StatusHistoryItem,
        SummaryHistoryItem,
        TagsHistoryItem,
        TermHistoryItem,
        TitleHistoryItem,
        TradeCategoryHistoryItem,
        TradeDirectionHistoryItem,
        TopPriorityStatusHistoryItem,
    )
    default_subclass = GenericHistoryItem
    class_lookup = {}


class ProgressUpdateHistoryItem(BaseHistoryItem):
    model = "progress_update"
    field = "status"
    field_name = "Delivery Confidence"
