ma.components.TextArea = (function (doc, jessie) {
    if (
        !jessie.hasFeatures(
            "attachListener",
            "bind",
            "queryOne",
            "addClass",
            "removeClass",
            "hasClass",
            "cancelDefault",
            "getElementData"
        )
    ) {
        return;
    }

    var queryOne = jessie.queryOne;
    var addClass = jessie.addClass;
    var removeClass = jessie.removeClass;
    var hasClass = jessie.hasClass;

    var ERROR_CLASS = ma.FORM_ERROR_CLASS;

    function TextArea(opts) {
        this.formGroup = queryOne(opts.group);
        this.input = queryOne(opts.input);

        if (!this.formGroup) {
            throw new Error("No form group found");
        }
        if (!this.input) {
            throw new Error("no input found");
        }

        this.error = queryOne(ERROR_CLASS, this.formGroup);
        this.inErrorState = !!this.error && hasClass(this.error, ERROR_CLASS);
    }

    TextArea.prototype.hasValue = function () {
        return this.input.value.length > 0;
    };

    TextArea.prototype.focus = function () {
        this.input.focus();
    };

    TextArea.prototype.setError = function (message) {
        if (!this.error) {
            this.error = doc.createElement("span");
            this.error.className = ERROR_CLASS;
        }

        this.error.innerText = message;
        this.input.parentNode.insertBefore(this.error, this.input);
        addClass(this.formGroup, ma.FORM_GROUP_ERROR_CLASS);
        addClass(this.input, ma.FORM_INPUT_ERROR_CLASS);
        this.inErrorState = true;
    };

    TextArea.prototype.removeError = function () {
        if (this.inErrorState) {
            this.error.parentNode.removeChild(this.error);
            removeClass(this.formGroup, ma.FORM_GROUP_ERROR_CLASS);
            removeClass(this.input, ma.FORM_INPUT_ERROR_CLASS);
            this.inErrorState = false;
        }
    };

    return TextArea;
})(document, jessie);
