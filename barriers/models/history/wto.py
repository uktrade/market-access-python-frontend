from .base import BaseHistoryItem, GenericHistoryItem
from .utils import PolymorphicBase
from barriers.models.wto import WTOProfile

import dateutil.parser


class CaseNumberHistoryItem(BaseHistoryItem):
    field = "case_number"
    field_name = "WTO dispute settlement case number"


class CommitteeNotificationDocumentHistoryItem(BaseHistoryItem):
    field = "committee_notification_document"
    field_name = "WTO committee notification document"


class CommitteeNotificationLinkHistoryItem(BaseHistoryItem):
    field = "committee_notification_link"
    field_name = "WTO committee notification"


class CommitteeNotifiedHistoryItem(BaseHistoryItem):
    field = "committee_notified"
    field_name = "WTO committee notified of the barrier"

    def get_value(self, value):
        return value.get("name")


class CommitteeRaisedInHistoryItem(BaseHistoryItem):
    field = "committee_raised_in"
    field_name = "WTO committee the barrier was raised in"

    def get_value(self, value):
        return value.get("name")


class MeetingMinutesHistoryItem(BaseHistoryItem):
    field = "meeting_minutes"
    field_name = "WTO committee meeting minutes"


class MemberStatesHistoryItem(BaseHistoryItem):
    field = "member_states"
    field_name = "WTO member states"

    def get_value(self, value):
        return [
            self.metadata.get_country(country_id).get("name")
            for country_id in value
        ]


class RaisedDateHistoryItem(BaseHistoryItem):
    field = "raised_date"
    field_name = "Date the barrier was raised in a bilateral meeting in Geneva"

    def get_value(self, value):
        if value:
            return dateutil.parser.parse(value)


class WTONotifiedStatusHistoryItem(BaseHistoryItem):
    field = "wto_notified_status"
    field_name = "WTO notified"

    def get_value(self, value):
        if value.get("wto_has_been_notified") is not None:
            wto_profile = WTOProfile(value)
            return wto_profile.status_text


class WTOHistoryItem(PolymorphicBase):
    """
    Polymorphic wrapper for HistoryItem classes
    """

    model = "wto_profile"
    key = "field"
    subclasses = (
        CaseNumberHistoryItem,
        CommitteeNotificationDocumentHistoryItem,
        CommitteeNotificationLinkHistoryItem,
        CommitteeNotifiedHistoryItem,
        CommitteeRaisedInHistoryItem,
        MeetingMinutesHistoryItem,
        MemberStatesHistoryItem,
        RaisedDateHistoryItem,
        WTONotifiedStatusHistoryItem,
    )
    default_subclass = GenericHistoryItem
    class_lookup = {}
