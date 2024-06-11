ma.components.Toast = (function (doc, jessie) {
    if (
        !jessie.hasFeatures(
            "attachListener",
            "bind",
            "queryOne",
            "cancelDefault"
        )
    ) {
        return;
    }

    function Toast(selector) {
        this.elem = jessie.queryOne(selector);

        if (!this.elem) {
            return;
        }

        this.createDismiss();
    }

    Toast.prototype.createDismiss = function () {
        this.dismissElem = doc.createElement("a");

        this.dismissElem.className = "toast__dismiss";
        this.dismissElem.href = "#";
        this.dismissElem.innerText = "x";

        jessie.attachListener(
            this.dismissElem,
            "click",
            this.dismiss.bind(this)
        );
        this.elem.appendChild(this.dismissElem);
    };

    Toast.prototype.dismiss = function (e) {
        jessie.cancelDefault(e);
        this.elem.parentNode.removeChild(this.elem);
    };

    return Toast;
})(document, jessie);
