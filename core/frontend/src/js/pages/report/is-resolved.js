ma.pages.report.isResolved = function (types) {
    if (!ma.components.ConditionalRadioContent) {
        return;
    }

    new ma.components.ConditionalRadioContent({
        inputContainer: ".is-resolved",
        inputName: "status",
        conditionalElem: "#conditional-" + types.RESOLVED,
        shouldShow: function (value) {
            return value == types.RESOLVED;
        },
    });

    new ma.components.ConditionalRadioContent({
        inputContainer: ".is-resolved",
        inputName: "status",
        conditionalElem: "#conditional-" + types.PART_RESOLVED,
        shouldShow: function (value) {
            return value == types.PART_RESOLVED;
        },
    });
};
