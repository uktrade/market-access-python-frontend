ma.components.Modal = (function (doc) {
    if (
        !jessie.hasFeatures(
            "bind",
            "addClass",
            "removeClass",
            "getEventTarget",
            "attachListener",
            "cancelDefault"
        )
    ) {
        return;
    }

    var MODAL_CANCEL_CLASS = "js-modal-cancel";
    var ESC_KEY = 27;

    var html =
        jessie.isHostObjectProperty(doc, "documentElement") &&
        doc.documentElement;
    var supportsCapturing = jessie.isHostMethod(html, "addEventListener");
    var supportsContains = jessie.isHostMethod(html, "contains");

    html = null;

    function Modal() {
        this.createBg();
        this.trapFocus();

        jessie.attachListener(
            doc,
            "keydown",
            jessie.bind(this.handeKeyDown, this)
        );
        jessie.attachListener(
            this.bg,
            "click",
            jessie.bind(this.handleBgClick, this)
        );
    }

    Modal.prototype.createBg = function () {
        this.bg = doc.createElement("div");
        this.bg.className = "modal";
    };

    Modal.prototype.open = function (modalContentElement) {
        this.activeElement = doc.activeElement;
        this.content = modalContentElement;
        this.bg.appendChild(this.content);

        doc.body.appendChild(this.bg);
        bodyScrollLock.disableBodyScroll(this.bg);
        this.content.focus();
        this.isOpen = true;
    };

    Modal.prototype.close = function () {
        bodyScrollLock.enableBodyScroll(this.bg);
        doc.body.removeChild(this.bg);
        this.activeElement.focus();
        this.activeElement = null;
        this.bg.innerHTML = "";
        this.isOpen = false;
    };

    Modal.prototype.trapFocus = function () {
        if (supportsCapturing && supportsContains) {
            doc.addEventListener(
                "focus",
                jessie.bind(this.handleFocus, this),
                true
            );
        }
    };

    Modal.prototype.handleFocus = function (e) {
        if (this.isOpen && !this.content.contains(e.target)) {
            e.stopPropagation();
            this.content.focus();
        }
    };

    Modal.prototype.handeKeyDown = function (e) {
        if (this.isOpen && e.keyCode === ESC_KEY) {
            this.close();
        }
    };

    Modal.prototype.handleBgClick = function (e) {
        var target = jessie.getEventTarget(e);

        if (target == this.bg || jessie.hasClass(target, MODAL_CANCEL_CLASS)) {
            jessie.cancelDefault(e);
            this.close();
        }
    };

    return Modal;
})(document);
