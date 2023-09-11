from barriers.models.history.base import BaseHistoryItem


class BarrierTopPrioritySummaryItem(BaseHistoryItem):
    model = "barrier_top_priority_summary"
    field = "top_priority_summary_text"
    field_name = "PB100 Rationale"