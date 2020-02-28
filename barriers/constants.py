from model_utils import Choices


class Statuses:
    UNFINISHED = "0"
    OPEN_PENDING_ACTION = "1"
    OPEN_IN_PROGRESS = "2"
    RESOLVED_IN_PART = "3"
    RESOLVED_IN_FULL = "4"
    DORMANT = "5"
    ARCHIVED = "6"
    UNKNOWN = "7"


ARCHIVED_REASON = Choices(
    ("DUPLICATE", "Duplicate"), ("NOT_A_BARRIER", "Not a barrier"), ("OTHER", "Other"),
)
