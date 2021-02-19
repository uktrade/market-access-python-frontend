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
    ("DUPLICATE", "Duplicate"),
    ("NOT_A_BARRIER", "Not a barrier"),
    ("OTHER", "Other"),
)


STATUSES = Choices(
    ("1", "OPEN_PENDING_ACTION", "Open: Pending action"),
    ("2", "OPEN_IN_PROGRESS", "Open: In progress"),
    ("3", "RESOLVED_IN_PART", "Resolved: In part"),
    ("4", "RESOLVED_IN_FULL", "Resolved: In full"),
    ("5", "DORMANT", "Dormant"),
)


ALL_STATUSES = (
    Choices(
        ("7", "UNKNOWN", "Unknown"),
    )
    + STATUSES
)


STATUSES_HELP_TEXT = Choices(
    (STATUSES.OPEN_PENDING_ACTION, "Barrier is awaiting action"),
    (STATUSES.OPEN_IN_PROGRESS, "Barrier is being worked on"),
    (
        STATUSES.RESOLVED_IN_PART,
        "Barrier impact has been significantly reduced but remains in part",
    ),
    (STATUSES.RESOLVED_IN_FULL, "Barrier has been resolved for all UK companies"),
    (STATUSES.DORMANT, "Barrier is present but not being pursued"),
)


UK_COUNTRY_ID = "80756b9a-5d95-e211-a939-e4115bead28a"


PUBLIC_BARRIER_STATUSES = Choices(
    (0, "UNKNOWN", "To be decided"),
    (10, "INELIGIBLE", "Not allowed"),
    (20, "ELIGIBLE", "Allowed"),
    (30, "READY", "Ready"),
    (40, "PUBLISHED", "Published"),
    (50, "UNPUBLISHED", "Unpublished"),
)
