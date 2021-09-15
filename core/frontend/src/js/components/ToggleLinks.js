ma.components.ToggleLinks = (function (doc, jessie) {
    var LINK_CLASS = "toggle-links-toggle";
    var LIST_CLASS = "toggle-links-list";
    var LIST_ITEM_CLASS = "toggle-links-list__item";

    if (
        !jessie.hasFeatures(
            "query",
            "attachListener",
            "bind",
            "cancelDefault",
            "getElementPositionStyles"
        )
    ) {
        return;
    }

    function ToggleLinks(opts) {
        if (!opts.text) {
            throw new Error("ToggleLinks needs text");
        }
        if (!opts.linkClass) {
            throw new Error("ToggleLinks needs linkClass");
        }

        this.links = jessie.query("." + opts.linkClass);

        if (!this.links.length) {
            return;
        }

        this.text = opts.text;
        this.visible = false;
        this.setupList();
        this.setupLink();
        this.setListPosition();

        jessie.attachListener(
            window,
            "resize",
            jessie.bind(this.setListPosition, this)
        );
    }

    ToggleLinks.prototype.setupList = function () {
        var listItem;
        var link;
        var i = 0;
        var firstLink = this.links[0];

        this.list = doc.createElement("ul");
        this.list.className = LIST_CLASS;
        this.list.style.display = "none";
        this.list.style.position = "absolute";

        firstLink.parentNode.insertBefore(this.list, firstLink);

        while ((link = this.links[i++])) {
            listItem = doc.createElement("li");
            listItem.className = LIST_ITEM_CLASS;
            listItem.appendChild(link);
            this.list.appendChild(listItem);
        }
    };

    ToggleLinks.prototype.setupLink = function () {
        var toggle = doc.createElement("a");

        toggle.href = "#";
        toggle.className = LINK_CLASS;
        toggle.innerText = this.text;
        jessie.attachListener(
            toggle,
            "click",
            jessie.bind(this.handleClick, this)
        );

        this.list.parentNode.insertBefore(toggle, this.list);
        this.toggle = toggle;
    };

    ToggleLinks.prototype.getTogglePosition = function () {
        var currentPosition = this.toggle.style.position;
        this.toggle.style.position = "static";
        var positions = jessie.getElementPositionStyles(this.toggle);
        this.toggle.style.position = currentPosition;

        return positions;
    };

    ToggleLinks.prototype.setListPosition = function () {
        if (!this.visible) {
            return;
        }

        var positions = this.getTogglePosition();
        var offset = this.toggle.offsetHeight;

        this.list.style.top = positions.top + "px";
        this.list.style.left = positions.left + "px";
        this.list.style.top = positions.top + offset + "px";
    };

    ToggleLinks.prototype.handleClick = function (e) {
        jessie.cancelDefault(e);

        var show = this.list.style.display === "none";

        this.list.style.display = show ? "" : "none";

        if (show) {
            this.visible = true;
            this.setListPosition();
        } else {
            this.toggle.blur();
            this.visible = false;
        }
    };

    return ToggleLinks;
})(document, jessie);
