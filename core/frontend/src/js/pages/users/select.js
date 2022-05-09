ma.pages.users = {
    enableGroupFilter: (function () {
        function bindOnSelectionChanged(event) {
            document
                .querySelector("#filter_group")
                .addEventListener("change", function (event) {
                    this.form.submit();
                });
        }

        return function () {
            bindOnSelectionChanged();
        };
    })(),
};
