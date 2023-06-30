ma.pages.report.statusWizardStep = function () {
    // Specify radio button
    const barrierStatusRadioOpen = document.getElementById("status-radio-2");
    const barrierStatusRadioPartial = document.getElementById("status-radio-3");
    const barrierStatusRadioResolved =
        document.getElementById("status-radio-4");

    // Onchange event for radio buttons
    barrierStatusRadioOpen.addEventListener("change", function () {
        updateStartDateHeading();
        updateDateFields();
    });
    barrierStatusRadioPartial.addEventListener("change", function () {
        updateStartDateHeading();
        updateDateFields();
    });
    barrierStatusRadioResolved.addEventListener("change", function () {
        updateStartDateHeading();
        updateDateFields();
    });

    // Specify start_date heading text section
    const startDateHeading = document.getElementById("start-date-heading");

    // Function to update hint text on start date question
    const updateStartDateHeading = function () {
        var selected = document.querySelector(
            'input[name="barrier-status-status"]:checked'
        );
        if (selected.value == 2) {
            startDateHeading.innerHTML =
                "When did or will the barrier start to affect trade?";
        } else {
            startDateHeading.innerHTML =
                "When did the barrier start to affect trade?";
        }
    };

    // Specify date inputs
    const barrierDateInputPartialMonth = document.getElementById(
        "status-date-group-barrier-status-partially_resolved_date_0"
    );
    const barrierDateInputPartialYear = document.getElementById(
        "status-date-group-barrier-status-partially_resolved_date_1"
    );
    const barrierDateInputResolvedMonth = document.getElementById(
        "status-date-group-barrier-status-resolved_date_0"
    );
    const barrierDateInputResolvedYear = document.getElementById(
        "status-date-group-barrier-status-resolved_date_1"
    );

    // Set storage dictionary for retrieval if switching status
    var storedDateVariables = {};

    // Function to update hint text on start date question
    const updateDateFields = function () {
        var selected = document.querySelector(
            'input[name="barrier-status-status"]:checked'
        );
        if (selected.value == 2) {
            // Open selected, clear all dates
            storeValue(barrierDateInputPartialMonth, "storedPartialMonth");
            storeValue(barrierDateInputPartialYear, "storedPartialYear");
            storeValue(barrierDateInputResolvedMonth, "storedResolvedMonth");
            storeValue(barrierDateInputResolvedYear, "storedResolvedYear");
            barrierDateInputPartialMonth.value = null;
            barrierDateInputPartialYear.value = null;
            barrierDateInputResolvedMonth.value = null;
            barrierDateInputResolvedYear.value = null;
            console.log(storedDateVariables);
        } else if (selected.value == 3) {
            // Partial resolve selected, clear resolved dates
            storeValue(barrierDateInputResolvedMonth, "storedResolvedMonth");
            storeValue(barrierDateInputResolvedYear, "storedResolvedYear");
            barrierDateInputPartialMonth.value =
                storedDateVariables["storedPartialMonth"];
            barrierDateInputPartialYear.value =
                storedDateVariables["storedPartialYear"];
            barrierDateInputResolvedMonth.value = null;
            barrierDateInputResolvedYear.value = null;
        } else {
            // Resolved selected, clear partial dates
            storeValue(barrierDateInputPartialMonth, "storedPartialMonth");
            storeValue(barrierDateInputPartialYear, "storedPartialYear");
            barrierDateInputPartialMonth.value = null;
            barrierDateInputPartialYear.value = null;
            barrierDateInputResolvedMonth.value =
                storedDateVariables["storedResolvedMonth"];
            barrierDateInputResolvedYear.value =
                storedDateVariables["storedResolvedYear"];
        }
    };

    const storeValue = function (input, storageVariable) {
        if (input.value != null && input.value != "") {
            storedDateVariables[storageVariable] = input.value;
        }
    };

    // Set initial value when page is loaded
    updateStartDateHeading();
};
