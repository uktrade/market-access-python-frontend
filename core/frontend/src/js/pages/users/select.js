ma.pages.users = {
    enableGroupFilter: function() {

        function bindOnSelectionChanged(event) {
            document.querySelector("#filter_group").addEventListener("change", function(event) {
                if (this.options[this.selectedIndex].value === 'all') {
                    self.location.href = `${self.location.origin}${self.location.pathname}`;
                } else {
                    this.form.submit();
                }
            })
        }

        return function() {
            bindOnSelectionChanged();
        };
    }(),
};