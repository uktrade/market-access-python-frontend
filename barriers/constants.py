from django.db.models import TextChoices
from model_utils import Choices


class Statuses:
    UNFINISHED = "0"
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
    ("2", "OPEN_IN_PROGRESS", "Open"),
    ("3", "RESOLVED_IN_PART", "Resolved: In part"),
    ("4", "RESOLVED_IN_FULL", "Resolved: In full"),
    ("5", "DORMANT", "Dormant"),
)

REPORTABLE_STATUSES = Choices(
    ("2", "OPEN_IN_PROGRESS", "Open"),
    ("3", "RESOLVED_IN_PART", "Resolved: In part"),
    ("4", "RESOLVED_IN_FULL", "Resolved: In full"),
)


STATUS_WITH_DATE_FILTER = [
    "open_in_progress",
    "resolved_in_part",
    "resolved_in_full",
]


ALL_STATUSES = (
    Choices(
        ("7", "UNKNOWN", "Unknown"),
    )
    + STATUSES
)


STATUSES_HELP_TEXT = Choices(
    (STATUSES.OPEN_IN_PROGRESS, "Barrier is being worked on, or work will begin soon"),
    (
        STATUSES.RESOLVED_IN_PART,
        "Barrier has been partially resolved and is still being worked on",
    ),
    (STATUSES.RESOLVED_IN_FULL, "Barrier has been fully resolved"),
)

REPORTABLE_STATUSES_HELP_TEXT = Choices(
    (
        REPORTABLE_STATUSES.OPEN_IN_PROGRESS,
        "Barrier is being worked on, or work will begin soon",
    ),
    (
        REPORTABLE_STATUSES.RESOLVED_IN_PART,
        "Barrier has been partially resolved and is still being worked on",
    ),
    (
        REPORTABLE_STATUSES.RESOLVED_IN_FULL,
        "Barrier has been fully resolved",
    ),
)


UK_COUNTRY_ID = "80756b9a-5d95-e211-a939-e4115bead28a"


PUBLIC_BARRIER_STATUSES = Choices(
    ("0", "UNKNOWN", "To be decided"),
    ("10", "NOT_ALLOWED", "Not allowed"),
    ("20", "ALLOWED", "Allowed"),
    ("70", "APPROVAL_PENDING", "Awaiting approval"),
    ("30", "PUBLISHING_PENDING", "Awaiting publishing"),
    ("40", "PUBLISHED", "Published"),
    ("50", "UNPUBLISHED", "Unpublished"),
)


ACTION_PLAN_TASK_CHOICES = Choices(
    ("NOT_STARTED", "Not started"),
    ("IN_PROGRESS", "In progress"),
    ("COMPLETED", "Completed"),
)

ACTION_PLAN_TASK_TYPE_CHOICES = Choices(
    ("SCOPING_AND_RESEARCH", "Scoping/Research"),
    ("LOBBYING", "Lobbying"),
    ("UNILATERAL_INTERVENTIONS", "Unilateral interventions"),
    ("BILATERAL_ENGAGEMENT", "Bilateral engagement"),
    ("PLURILATERAL_ENGAGEMENT", "Plurilateral engagement"),
    ("MULTILATERAL_ENGAGEMENT", "Multilateral engagement"),
    ("EVENT", "Event"),
    ("WHITEHALL_FUNDING_STREAMS", "Whitehall funding streams"),
    ("RESOLUTION_NOT_LEAD_BY_DIT", "Resolution not lead by DIT"),
    ("OTHER", "Other"),
)

ACTION_PLAN_TASK_CATEGORIES = {
    ACTION_PLAN_TASK_TYPE_CHOICES.SCOPING_AND_RESEARCH: Choices(
        *[
            "Dialogue",
            "Stakeholder mapping",
            "Research",
            "Awareness raising",
            "Comparing with similar barriers",
            "Analysis",
            "Best practise workshops",
            "Investigating possible workarounds",
            "Other",
        ]
    ),
    ACTION_PLAN_TASK_TYPE_CHOICES.LOBBYING: Choices(
        *[
            "Lobbying by officials",
            "Lobbying by ministers",
            "Lobbying by experts",
            "Lobbying by industry",
            "Lobbying with PM office",
            "Lobbying by OGD",
            "Influencing standard-setting bodies",
            "Other",
        ]
    ),
    ACTION_PLAN_TASK_TYPE_CHOICES.UNILATERAL_INTERVENTIONS: Choices(
        *[
            "Technical support to UK",
            "Support to partner country",
            "Export finance",
            "Public consultation",
            "Legislative changes",
            "Harmonise standards",
            "Trade remedies/disputes",
            "Other",
        ]
    ),
    ACTION_PLAN_TASK_TYPE_CHOICES.BILATERAL_ENGAGEMENT: Choices(
        *[
            "Creating and maintaining trade agreements",
            "Building partnerships",
            "Market liberalisation forums",
            "Other",
        ]
    ),
    ACTION_PLAN_TASK_TYPE_CHOICES.PLURILATERAL_ENGAGEMENT: Choices(
        *[
            "With the EU",
            "With other forums",
            "Other",
        ]
    ),
    ACTION_PLAN_TASK_TYPE_CHOICES.MULTILATERAL_ENGAGEMENT: Choices(
        *[
            "With OECD",
            "With UN",
            "With WHO",
            "With G20/G7",
            "With WTO",
            "Other",
        ]
    ),
    ACTION_PLAN_TASK_TYPE_CHOICES.EVENT: Choices(
        *[
            "Organised exhibition",
            "Conference",
            "Trade delegation",
            "Roundtable",
            "Other",
        ]
    ),
    ACTION_PLAN_TASK_TYPE_CHOICES.WHITEHALL_FUNDING_STREAMS: Choices(
        *[
            "Prosperity fund",
            "Offical development assistance (ODA)",
            "Other",
        ]
    ),
    ACTION_PLAN_TASK_TYPE_CHOICES.RESOLUTION_NOT_LEAD_BY_DIT: Choices(
        *[
            "Lead by OGDs",
            "Lead by industry",
            "Other",
        ]
    ),
    ACTION_PLAN_TASK_TYPE_CHOICES.OTHER: None,
}

ACTION_PLAN_RAG_STATUS_CHOICES = Choices(
    ("ON_TRACK", "On track"),
    ("RISK_OF_DELAY", "Risk of delay"),
    ("DELAYED", "Delayed"),
)

ACTION_PLAN_RISK_LEVEL_CHOICES = Choices(
    ("LOW", "Low"),
    ("MEDIUM", "Medium"),
    ("HIGH", "High"),
)

ACTION_PLAN_STAKEHOLDER_TYPE_CHOICES = TextChoices(
    "ACTION_PLAN_STAKEHOLDER_TYPE_CHOICES", "INDIVIDUAL ORGANISATION"
)

ACTION_PLAN_STAKEHOLDER_STATUS_CHOICES = TextChoices(
    "ACTION_PLAN_STAKEHOLDER_STATUS_CHOICES", "FRIEND NEUTRAL TARGET BLOCKER"
)

ACTION_PLAN_RISK_LEVEL_CHOICES = Choices(
    ("LOW", "Low"),
    ("MEDIUM", "Medium"),
    ("HIGH", "High"),
)

ACTION_PLAN_HAS_RISKS_CHOICES = Choices(
    ("YES", "Yes"),
    ("NO", "No"),
)

ACTION_PLAN_STAKEHOLDER_TYPE_CHOICES = TextChoices(
    "ACTION_PLAN_STAKEHOLDER_TYPE_CHOICES", "INDIVIDUAL ORGANISATION"
)

ACTION_PLAN_STAKEHOLDER_STATUS_CHOICES = TextChoices(
    "ACTION_PLAN_STAKEHOLDER_STATUS_CHOICES", "FRIEND NEUTRAL TARGET BLOCKER"
)

TOP_PRIORITY_BARRIER_STATUS = Choices(
    ("NONE", ""),
    ("APPROVAL_PENDING", "Top 100 Priority Approval Pending"),
    ("REMOVAL_PENDING", "Top 100 Priority Removal Pending"),
    ("APPROVED", "Top 100 Priority"),
    ("RESOLVED", "Top 100 Priority Resolved"),
)

TOP_PRIORITY_BARRIER_STATUS_REQUEST_APPROVAL_CHOICES = Choices(
    ("APPROVAL_PENDING", "Yes"),
    ("NONE", "No"),
)

TOP_PRIORITY_BARRIER_STATUS_REQUEST_REMOVAL_CHOICES = Choices(
    ("APPROVED", "Yes"),
    ("REMOVAL_PENDING", "No"),
)

# Default choice field for a user that can moderate top priority
TOP_PRIORITY_BARRIER_STATUS_APPROVAL_CHOICES = Choices(
    ("APPROVED", "Yes"),
    ("NONE", "No"),
)

TOP_PRIORITY_BARRIER_STATUS_APPROVE_REQUEST_CHOICES = Choices(
    ("APPROVED", "Yes"),  # Set to APPROVED when Yes is selected
    ("NONE", "No"),
)

TOP_PRIORITY_BARRIER_STATUS_APPROVE_REMOVAL_CHOICES = Choices(
    ("NONE", "Yes"),  # Set to NONE when Yes is selected
    ("APPROVED", "No"),
)

TOP_PRIORITY_BARRIER_STATUS_RESOLVED_CHOICES = Choices(
    ("APPROVAL_PENDING", "Yes"),  # Would need approval to put back to top priority
    ("RESOLVED", "No"),  # Keep as a resolved barrier
)

TOP_PRIORITY_BARRIER_EDIT_PERMISSION = "set_topprioritybarrier"

# Deprecated tags are tags we do not want future barriers to be able to use,
# but need to keep for older and archived barriers.
DEPRECATED_TAGS = ("COVID-19", "Brexit", "NI Protocol", "Programme Fund")

EXPORT_TYPES = Choices(
    ("goods", "Goods"),
    ("services", "Services"),
    ("investments", "Investments"),
)

# Related barriers rag tags
RELATED_BARRIER_TAGS = {
    "duplicate": {
        "lower_boundary": 0.9,
        "upper_boundary": 2,
        "label": "Potential duplicate",
        "class": "govuk-tag--green",
    },
    "similar": {
        "lower_boundary": 0.7,
        "upper_boundary": 0.9,
        "label": "Very similar",
        "class": "govuk-tag--turquoise",
    },
    "good": {
        "lower_boundary": 0.4,
        "upper_boundary": 0.7,
        "label": "Good match",
        "class": "govuk-tag--blue",
    },
    "some": {
        "lower_boundary": 0.2,
        "upper_boundary": 0.4,
        "label": "Some relevance",
        "class": "govuk-tag--purple",
    },
    "poor": {
        "lower_boundary": 0,
        "upper_boundary": 0.2,
        "label": "Poor match",
        "class": "govuk-tag--pink",
    },
}
