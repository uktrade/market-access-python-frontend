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


STATUSES = Choices(
    ("7", "UNKNOWN", "Unknown"),
    ("1", "OPEN_PENDING_ACTION", "Open: Pending action"),
    ("2", "OPEN_IN_PROGRESS", "Open: In progress"),
    ("3", "RESOLVED_IN_PART", "Resolved: In part"),
    ("4", "RESOLVED_IN_FULL", "Resolved: In full"),
    ("5", "DORMANT", "Dormant"),
)


STATUSES_HELP_TEXT = Choices(
    (STATUSES.UNKNOWN, "Barrier requires further work for the status to be known"),
    (STATUSES.OPEN_PENDING_ACTION, "Barrier is awaiting action"),
    (STATUSES.OPEN_IN_PROGRESS, "Barrier is being worked on"),
    (
        STATUSES.RESOLVED_IN_PART,
        "Barrier impact has been significantly reduced but remains in part"
    ),
    (STATUSES.RESOLVED_IN_FULL, "Barrier has been resolved for all UK companies"),
    (STATUSES.DORMANT, "Barrier is present but not being pursued"),
)
