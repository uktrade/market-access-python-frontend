ma.components.ConditionalRadioContent = (function (jessie) {
    if (
        !jessie.hasFeatures(
            "bind",
            "query",
            "queryOne",
            "addClass",
            "removeClass",
            "setAriaAttribute",
            "attachListener",
            "getInputValue"
        )
    ) {
        return;
    }

    var bind = jessie.bind;
    var query = jessie.query;
    var queryOne = jessie.queryOne;
    var attachListener = jessie.attachListener;
    var addClass = jessie.addClass;
    var removeClass = jessie.removeClass;
    var setAriaAttribute = jessie.setAriaAttribute;
    var getInputValue = jessie.getInputValue;

    var govukClass = "govuk-radios__conditional--hidden";

    function ConditionalRadioContent(opts) {
        if (!opts.inputName) {
            throw new Error("inputName is required");
        }
        if (!opts.inputContainer) {
            throw new Error("inputContainer is required");
        }
        if (!opts.conditionalElem) {
            throw new Error("conditionalElem is required");
        }
        if (!opts.shouldShow) {
            throw new Error("shouldShow is required");
        }

        this.inputContainer = queryOne(opts.inputContainer);
        this.inputName = opts.inputName;
        this.conditionalElem = queryOne(opts.conditionalElem);
        this.shouldShow = opts.shouldShow;
        this.events = {
            toggle: new ma.CustomEvent(),
        };

        if (!this.inputContainer) {
            throw new Error("inputContainer not found");
        }

        var inputs = query(".govuk-radios__input", this.inputContainer);
        var input;
        var i = 0;

        if (!this.conditionalElem || !inputs.length) {
            return;
        }

        this.conditionalElemId = this.conditionalElem.getAttribute("id");
        addClass(this.conditionalElem, "visually-hidden");
        removeClass(this.conditionalElem, govukClass); // remove this class as it keeps the content hidden
        setAriaAttribute(this.conditionalElem, "hidden", true);

        // Set "display: none" explicitly to prevent tabbing into hidden elements
        this.conditionalElem.setAttribute("style", "display: none");

        while ((input = inputs[i++])) {
            attachListener(input, "click", bind(this.checkState, this));

            if (this.shouldShow(getInputValue(input))) {
                setAriaAttribute(input, "controls", this.conditionalElemId);
            }
        }

        this.checkState();
    }

    ConditionalRadioContent.prototype.toggleConditional = function (show) {
        var classFn = show ? "removeClass" : "addClass";

        jessie[classFn](this.conditionalElem, "visually-hidden");
        setAriaAttribute(this.conditionalElem, "hidden", !show);

        if (show) {
            this.conditionalElem.removeAttribute("style");
        } else {
            this.conditionalElem.setAttribute("style", "display: none");
        }
        this.events.toggle.publish(show);
    };

    ConditionalRadioContent.prototype.checkState = function (/* e */) {
        var checked = queryOne(
            'input[ name="' + this.inputName + '" ]:checked',
            this.inputContainer
        );

        if (checked) {
            var value = checked && getInputValue(checked);
            var show = this.shouldShow(value);
            this.toggleConditional(show);
        }
    };

    return ConditionalRadioContent;
})(jessie);
