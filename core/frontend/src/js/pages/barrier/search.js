ma.pages.barrier.search = (function (doc) {
    let searchSelect = document.querySelector(".dmas-search-ordering-select");
    searchSelect.addEventListener("change", function (event) {
        this.form.submit();
    });
    return {
        searchSelect: searchSelect,
    };
})(document);
