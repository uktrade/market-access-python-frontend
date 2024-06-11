ma.pages.barrier.action_plans_add_task = function () {
    if (!ma.components.ConditionalRadioContent) {
        return;
    }

    new ma.components.ConditionalRadioContent({
        inputContainer: ".status",
        inputName: "status",
        conditionalElem: "#conditional-IN_PROGRESS",
        shouldShow: function (value) {
            return value === "IN_PROGRESS";
        },
    });

    new ma.components.ConditionalRadioContent({
        inputContainer: ".status",
        inputName: "status",
        conditionalElem: "#conditional-COMPLETED",
        shouldShow: function (value) {
            return value === "COMPLETED";
        },
    });

    new ma.components.ConditionalRadioContent({
        inputContainer: ".action_type",
        inputName: "action_type",
        conditionalElem: "#conditional-SCOPING_AND_RESEARCH",
        shouldShow: function (value) {
            return value === "SCOPING_AND_RESEARCH";
        },
    });

    new ma.components.ConditionalRadioContent({
        inputContainer: ".action_type",
        inputName: "action_type",
        conditionalElem: "#conditional-LOBBYING",
        shouldShow: function (value) {
            return value === "LOBBYING";
        },
    });

    new ma.components.ConditionalRadioContent({
        inputContainer: ".action_type",
        inputName: "action_type",
        conditionalElem: "#conditional-UNILATERAL_INTERVENTIONS",
        shouldShow: function (value) {
            return value === "UNILATERAL_INTERVENTIONS";
        },
    });

    new ma.components.ConditionalRadioContent({
        inputContainer: ".action_type",
        inputName: "action_type",
        conditionalElem: "#conditional-BILATERAL_ENGAGEMENT",
        shouldShow: function (value) {
            return value === "BILATERAL_ENGAGEMENT";
        },
    });

    new ma.components.ConditionalRadioContent({
        inputContainer: ".action_type",
        inputName: "action_type",
        conditionalElem: "#conditional-PLURILATERAL_ENGAGEMENT",
        shouldShow: function (value) {
            return value === "PLURILATERAL_ENGAGEMENT";
        },
    });

    new ma.components.ConditionalRadioContent({
        inputContainer: ".action_type",
        inputName: "action_type",
        conditionalElem: "#conditional-MULTILATERAL_ENGAGEMENT",
        shouldShow: function (value) {
            return value === "MULTILATERAL_ENGAGEMENT";
        },
    });

    new ma.components.ConditionalRadioContent({
        inputContainer: ".action_type",
        inputName: "action_type",
        conditionalElem: "#conditional-EVENT",
        shouldShow: function (value) {
            return value === "EVENT";
        },
    });

    new ma.components.ConditionalRadioContent({
        inputContainer: ".action_type",
        inputName: "action_type",
        conditionalElem: "#conditional-WHITEHALL_FUNDING_STREAMS",
        shouldShow: function (value) {
            return value === "WHITEHALL_FUNDING_STREAMS";
        },
    });

    new ma.components.ConditionalRadioContent({
        inputContainer: ".action_type",
        inputName: "action_type",
        conditionalElem: "#conditional-RESOLUTION_NOT_LEAD_BY_DIT",
        shouldShow: function (value) {
            return value === "RESOLUTION_NOT_LEAD_BY_DIT";
        },
    });

    new ma.components.ConditionalRadioContent({
        inputContainer: ".action_type",
        inputName: "action_type",
        conditionalElem: "#conditional-OTHER",
        shouldShow: function (value) {
            return value === "OTHER";
        },
    });
};
