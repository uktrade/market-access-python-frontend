ma.pages.report.hiddenRadioContent = function () {
    const showComponent = function (component) {
        component.classList.remove("govuk-radios__conditional--hidden");
        // component.style.visibility = "visible";
    };
    const hideComponent = function (component) {
        component.classList.add("govuk-radios__conditional--hidden");
        // component.style.visibility = "hidden";
    };

    const updateComponents = function (id) {
        conditionalComponents.forEach(function (currentConditionalComponent) {
            if (currentConditionalComponent.id == "conditional-" + id) {
                showComponent(currentConditionalComponent);
            } else {
                hideComponent(currentConditionalComponent);
            }
        });
    };

    const conditionalComponents = document.querySelectorAll(
        ".govuk-radios__conditional",
    );
    const radioButtons = document.querySelectorAll(".govuk-radios__input");

    radioButtons.forEach(function (currentRadioButton) {
        showComponent(currentRadioButton);
        currentRadioButton.addEventListener("click", function () {
            updateComponents(this.id);
        });
    });
};
