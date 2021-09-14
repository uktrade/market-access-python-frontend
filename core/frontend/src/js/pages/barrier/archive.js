ma.pages.barrier.archive = function () {
    if (!ma.components.ConditionalRadioContent) {
        return;
    }

    new ma.components.ConditionalRadioContent({
        inputContainer: ".reason",
        inputName: "reason",
        conditionalElem: "#conditional-DUPLICATE",
        shouldShow: function (value) {
            return value === "DUPLICATE";
        },
    });

    new ma.components.ConditionalRadioContent({
        inputContainer: ".reason",
        inputName: "reason",
        conditionalElem: "#conditional-NOT_A_BARRIER",
        shouldShow: function (value) {
            return value === "NOT_A_BARRIER";
        },
    });

    new ma.components.ConditionalRadioContent({
        inputContainer: ".reason",
        inputName: "reason",
        conditionalElem: "#conditional-OTHER",
        shouldShow: function (value) {
            return value === "OTHER";
        },
    });
};
