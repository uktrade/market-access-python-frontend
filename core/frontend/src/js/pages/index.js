ma.pages.index = (function () {
    return function () {
        if (ma.components.Collapsible) {
            ma.components.Collapsible.initAll();
        }
    };
})();
