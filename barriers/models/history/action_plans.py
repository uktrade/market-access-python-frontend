from barriers.models.history.base import BaseHistoryItem, GenericHistoryItem
from barriers.models.history.utils import PolymorphicBase


class CurrentStatusLastUpdatedHistoryItem(BaseHistoryItem):
    field = "current_status_last_updated"
    field_name = "Current status last updated"


class CurrentStatusHistoryItem(BaseHistoryItem):
    field = "current_status"
    field_name = "Current status"


class StatusHistoryItem(BaseHistoryItem):
    field = "status"
    field_name = "Status"


class StrategicContextHistoryItem(BaseHistoryItem):
    field = "strategic_context"
    field_name = "Strategic context"


class ActionPlanHistoryItem(PolymorphicBase):
    """
    Polymorphic wrapper for HistoryItem classes
    """

    model = "action_plan"
    key = "field"
    subclasses = (
        CurrentStatusLastUpdatedHistoryItem,
        CurrentStatusHistoryItem,
        StatusHistoryItem,
        StrategicContextHistoryItem,
    )
    default_subclass = GenericHistoryItem
    class_lookup = {}


class ObjectiveHistoryItem(BaseHistoryItem):
    field = "objective"
    field_name = "Objective"


class CompletionDateHistoryItem(BaseHistoryItem):
    field = "completion_date"
    field_name = "Completion date"


class ActionPlanMilestoneHistoryItem(PolymorphicBase):
    """
    Polymorphic wrapper for HistoryItem classes
    """

    model = "action_plan_milestone"
    key = "field"
    subclasses = (ObjectiveHistoryItem, CompletionDateHistoryItem)
    default_subclass = GenericHistoryItem
    class_lookup = {}


class StatusHistoryItem(BaseHistoryItem):
    field = "status"
    field_name = "Status"


class StartDateHistoryItem(BaseHistoryItem):
    field = "start_date"
    field_name = "Start Date"


class CompletionDateHistoryItem(BaseHistoryItem):
    field = "completion_date"
    field_name = "Completion Date"


class ActionTextHistoryItem(BaseHistoryItem):
    field = "action_text"
    field_name = "Action text"


class ActionTypeCategoryHistoryItem(BaseHistoryItem):
    field = "action_type_category"
    field_name = "Action type category"


class AssignedToHistoryItem(BaseHistoryItem):
    field = "assigned_to"
    field_name = "Assigned to"


class StakeholdersHistoryItem(BaseHistoryItem):
    field = "stakeholders"
    field_name = "Stakeholders"


class ProgressHistoryItem(BaseHistoryItem):
    field = "progress"
    field_name = "Progress"


class OutcomeHistoryItem(BaseHistoryItem):
    field = "outcome"
    field_name = "Outcome"


class ActionPlanTaskHistoryItem(PolymorphicBase):
    """
    Polymorphic wrapper for HistoryItem classes
    """

    model = "action_plan_task"
    key = "field"
    subclasses = (
        StatusHistoryItem,
        ActionTextHistoryItem,
        ActionTypeCategoryHistoryItem,
        AssignedToHistoryItem,
        StakeholdersHistoryItem,
        ProgressHistoryItem,
        OutcomeHistoryItem,
        StartDateHistoryItem,
        CompletionDateHistoryItem,
    )
    default_subclass = GenericHistoryItem
    class_lookup = {}
