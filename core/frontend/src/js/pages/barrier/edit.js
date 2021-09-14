ma.pages.barrier.edit = {
    title: function () {
        if (!(jessie.queryOne && jessie.attachListener)) {
            return;
        }

        var heading = jessie.queryOne(".js-heading-caption");
        var input = jessie.queryOne("input[name=title]");

        if (input && heading) {
            jessie.attachListener(input, "keyup", function () {
                heading.innerText = input.value;
            });
        }
    },

    source: function () {
        if (!ma.components.ConditionalRadioContent) {
            return;
        }

        new ma.components.ConditionalRadioContent({
            inputContainer: ".source",
            inputName: "source",
            conditionalElem: "#conditional-OTHER",
            shouldShow: function (value) {
                return value === "OTHER";
            },
        });
    },
};
