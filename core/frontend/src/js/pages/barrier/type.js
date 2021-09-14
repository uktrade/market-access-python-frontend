ma.pages.barrier.type = (function (doc) {
    return function () {
        if (!ma.components.ConditionalRadioContent) {
            return;
        }

        var container = ".category";
        var inputName = "category";
        var conditional;
        var i = 0;

        var conditionals = doc.querySelectorAll(".govuk-radios__conditional");

        while ((conditional = conditionals[i++])) {
            var inputId = conditional.id.replace("conditional-", "");
            var input = doc.querySelector("#" + inputId);

            (function (inputValue) {
                new ma.components.ConditionalRadioContent({
                    inputContainer: container,
                    inputName: inputName,
                    conditionalElem: "#" + conditional.id,
                    shouldShow: function (value) {
                        return value === inputValue;
                    },
                });
            })(input.value);
        }
    };
})(document);
