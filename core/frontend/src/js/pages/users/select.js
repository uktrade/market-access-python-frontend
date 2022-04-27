ma.pages.users = {
    select: function() {

        function bindOnSelectionChanged(event) {
            document.querySelector("#filter_group").addEventListener("change", function(event) {
                debugger;
            })
        }

        return function() {
            bindOnSelectionChanged();
        };
    }(),
};