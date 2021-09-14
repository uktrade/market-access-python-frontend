ma.pages.report.aboutProblem = function () {
    if (!ma.components.ConditionalRadioContent) {
        return;
    }

    new ma.components.ConditionalRadioContent({
        inputContainer: ".barrier-source",
        inputName: "source",
        conditionalElem: "#conditional-OTHER",
        shouldShow: function (value) {
            return value === "OTHER";
        },
    });
};
