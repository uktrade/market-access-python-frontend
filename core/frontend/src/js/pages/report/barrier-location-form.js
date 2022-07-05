const hideShowExtraInputsOnCountryChange = () => {
    const countrySelectInputId = "location";
    const countrySelectInput = document.querySelector(
        `select[name='${countrySelectInputId}']`
    );
    const currentlySelectedCountry = countrySelectInput.value;
    console.log(
        "currentlySelectedCountry",
        currentlySelectedCountry,
        document.getElementById(countrySelectInputId)
    );
    const additionalFieldsContainer = document.getElementById(
        "additional-location-fields"
    );
    countrySelectInput.addEventListener("change", () => {
        if (!additionalFieldsContainer) return;
        const newCountry = countrySelectInput.value;
        if (currentlySelectedCountry != newCountry) {
            // Hide all extra fields
            additionalFieldsContainer.style.display = "none";
        } else {
            additionalFieldsContainer.style.display = "block";
        }
    });
};

ma.pages.report.locationFormInit = () => {
    console.log("initializing location form");
    const adminAreasSelectInputId = "admin_areas";
    const addAdminAreaButtonName = "add_admin_area";
    const addAdminAreaButton = document.getElementById(addAdminAreaButtonName);
    const adminAreasSelectInput = document.getElementById(
        adminAreasSelectInputId
    );
    const adminAreaSelected = adminAreasSelectInput?.value;
    console.log("adminAreaSelected", adminAreaSelected);

    const shouldUseAdminAreaRadioName = "has_admin_areas";

    const adminAreaSelectContainer = document.getElementById(
        "admin-area-select-container"
    );
    const selectedAdminAreasContainer = document.getElementById(
        "selected-admin-areas-container"
    );

    hideShowExtraInputsOnCountryChange();

    // const countrySelectInputId = "location";
    // const countrySelectInput = document.querySelector(
    //     `select[name='location']`
    // );
    // const currentlySelectedCountry = countrySelectInput.value;
    // console.log(
    //     "currentlySelectedCountry",
    //     currentlySelectedCountry,
    //     document.getElementById(countrySelectInputId)
    // );
    // countrySelectInput.addEventListener("change", () => {
    //     const newCountry = countrySelectInput.value;
    //     if (currentlySelectedCountry != newCountry) {
    //         // Hide all extra fields
    //         document.getElementById(
    //             "additional-location-fields"
    //         ).style.display = "none";
    //     } else {
    //         document.getElementById(
    //             "additional-location-fields"
    //         ).style.display = "block";
    //     }
    // });

    const getShouldUseAdminAreaRadioValue = () => {
        const shouldUseAdminAreaRadio = document.querySelector(
            `input[name="${shouldUseAdminAreaRadioName}"]:checked`
        );
        return shouldUseAdminAreaRadio?.value;
    };

    const showHideAdminAreaSelect = () => {
        if (!adminAreaSelectContainer) {
            return;
        }
        const shouldUseAdminArea = getShouldUseAdminAreaRadioValue();
        if (shouldUseAdminArea === "2") {
            adminAreaSelectContainer.style.display = "block";
            if (selectedAdminAreasContainer) {
                selectedAdminAreasContainer.style.display = "block";
            }
        } else {
            adminAreaSelectContainer.style.display = "none";
            if (selectedAdminAreasContainer) {
                selectedAdminAreasContainer.style.display = "none";
            }
        }
    };
    showHideAdminAreaSelect();

    if (!adminAreaSelected && addAdminAreaButton) {
        // Hide the add admin area button if no admin area is selected
        addAdminAreaButton.style.display = "none";
    }

    const shouldUseAdminAreaRadios = document.querySelectorAll(
        `input[name="${shouldUseAdminAreaRadioName}"]`
    );
    for (let i = 0; i < shouldUseAdminAreaRadios.length; i++) {
        const radio = shouldUseAdminAreaRadios[i];
        radio.addEventListener("change", () => {
            const shouldUseAdminAreaRadioValue =
                getShouldUseAdminAreaRadioValue();
            console.log("radios changed", shouldUseAdminAreaRadioValue);
            showHideAdminAreaSelect();
        });
    }

    // debugger;
    // listen for changes to the admin area select input
    adminAreasSelectInput?.addEventListener("change", () => {
        const adminAreaSelected = adminAreasSelectInput?.value;
        if (!addAdminAreaButton) return;
        console.log("adminAreaSelected", adminAreaSelected);
        // update the location form
        if (adminAreaSelected) {
            // show the add admin area button
            addAdminAreaButton.style.display = "block";
        } else {
            addAdminAreaButton.style.display = "none";
        }
    });
};
