ma.components.DeleteModal = (function () {
    if (
        !(
            jessie.hasFeatures(
                "bind",
                "ajaxGet",
                "hasClass",
                "getEventTarget",
                "attachListener",
                "cancelDefault",
                "queryOne"
            ) || ma.components.Modal
        )
    ) {
        return;
    }

    var MODAL_CLASS = "js-delete-modal";

    function DeleteModal() {
        var container = jessie.queryOne(".js-delete-modal-container");

        if (!container) {
            return;
        }

        this.modal = new ma.components.Modal();
        jessie.attachListener(
            container,
            "click",
            jessie.bind(this.handleClick, this)
        );
    }

    DeleteModal.prototype.handleClick = function (e) {
        var target = jessie.getEventTarget(e);
        var useModal = jessie.hasClass(target, MODAL_CLASS);
        var modal = this.modal;

        if (!useModal || modal.isOpen) {
            return;
        }

        var url = target.href;

        jessie.cancelDefault(e);

        jessie.ajaxGet(url, {
            success: function (data) {
                try {
                    var wrapper = document.createElement("div");
                    wrapper.innerHTML = data;
                    modal.open(jessie.queryOne(".modal__content", wrapper));
                    wrapper = null;
                } catch (e) {
                    window.location.href = url;
                }
            },

            fail: function () {
                window.location.href = url;
            },
        });
    };

    return DeleteModal;
})();
