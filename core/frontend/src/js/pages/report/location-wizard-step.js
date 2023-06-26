ma.pages.report.locationWizardStep = function (trading_bloc_countries) {
    // Functions to show/hide individual page componenets
    const showComponent = function (component) {
        if (component != null) {
            component.classList.remove("govuk-visually-hidden");
        }
    };
    const hideComponent = function (component) {
        if (component != null) {
            component.classList.add("govuk-visually-hidden");
        }
    };

    const tradingBlocSection = document.getElementById("trading-bloc-section");
    const adminAreaSection = document.getElementById("admin-area-section");

    // Code to run on page load
    document.addEventListener("readystatechange", function (event) {
        if (document.readyState === "complete") {
            // Get details of selected country
            var countrySelectedId = countrySelector.value;
            var countrySelectedName =
                countrySelector.options[countrySelector.selectedIndex].text;

            handleTradingBlocSection(countrySelectedId);
            handleAdminAreaSection(countrySelectedName, "False");
        }
    });

    // Setup arrays to track selected admin areas
    const selectedAdminAreasNames = [];
    const selectedAdminAreasIds = [];

    // Get selected country on location_select change
    // The section in the selector component
    const countrySection = document.getElementById("location_select");
    // The actual select element of the component
    const countrySelector = document.getElementsByName(
        "barrier-location-location_select"
    )[0];

    // Run checks when change detected in location selector component
    countrySection.addEventListener("change", function () {
        // Get details of selected country
        var countrySelectedId = countrySelector.value;
        var countrySelectedName =
            countrySelector.options[countrySelector.selectedIndex].text;
        // Call handle functions to show/hide sections.
        handleTradingBlocSection(countrySelectedId);
        handleAdminAreaSection(countrySelectedName, "True");
    });

    const handleTradingBlocSection = function (countrySelectedId) {
        // Show trading bloc question if selected country in a trading bloc list
        // 1. Convert passed data to object of JS's understanding
        let tradingBlocsCountriesList = trading_bloc_countries.replace(
            /'/g,
            '"'
        );
        var tradingBlocsCountriesJson = JSON.parse(tradingBlocsCountriesList);
        // 2. Loop the trading bloc lists
        for (const [key, value] of Object.entries(tradingBlocsCountriesJson)) {
            // 3. Hide the question
            const tradingBlocQuestion = document.getElementById(
                "trading_bloc_" + key
            );
            // 4. Hide the question to clear options already being displayed
            hideComponent(tradingBlocQuestion);
            if (value.includes(countrySelectedId)) {
                // 5. If the country is in the current list, show the section and question
                showComponent(tradingBlocSection);
                showComponent(tradingBlocQuestion);
            }
        }
    };

    const handleAdminAreaSection = function (countrySelectedName, reset) {
        // Show admin areas question if selected country has admin areas
        // 1. Hide all admin area selectors;
        const adminAreaSelectors = document.getElementsByName(
            "admin-area-selector-section"
        );
        for (var x = 0; x < adminAreaSelectors.length; x++) {
            hideComponent(adminAreaSelectors[x]);
        }

        // 2. Clear admin area inputs, or load in existing values
        if (reset == "True") {
            // This route is taken when selecting a new country
            const adminAreasInput = document.getElementById(
                "admin-areas-selection-input"
            );
            adminAreasInput.value = "";
            selectedAdminAreasNames.length = 0;
            selectedAdminAreasIds.length = 0;
        } else {
            // This route is taken when entering the page
            const adminAreasInput = document.getElementById(
                "admin-areas-selection-input"
            );
            var adminAreasInputValue = adminAreasInput.value.split(",");
            for (let i = 0; i < adminAreasInputValue.length; i++) {
                if (adminAreasInputValue[i] != "") {
                    selectedAdminAreasIds.push(adminAreasInputValue[i]);
                }
            }
            // get the selection box, find the name for the area base on the list of selections and compare the value
            const adminAreaSelector = document.getElementById(
                "admin_areas_" + countrySelectedName
            );
            if (adminAreaSelector) {
                adminAreas = adminAreaSelector.children;
                for (i = 0; i < adminAreas.length; i++) {
                    adminAreas[i].innerHTML;
                    if (selectedAdminAreasIds.includes(adminAreas[i].value)) {
                        selectedAdminAreasNames.push(adminAreas[i].innerHTML);
                    }
                }
            }

            // pre-select the reveal option if there are admin-areas selected
            const adminAreaReveal =
                document.getElementById("admin-area-reveal");
            if (selectedAdminAreasIds.length > 0) {
                adminAreaReveal.setAttribute("checked", "checked");
            }
        }

        // 3. Update the selections list area
        updateSelectedAdminAreasContainer(
            selectedAdminAreasNames,
            selectedAdminAreasIds
        );

        // 4. Get the selector element for the selected country
        const adminAreaForCountry = document.getElementById(
            "admin_areas_" + countrySelectedName + "-section"
        );
        // 5. If the element exists, display it
        if (adminAreaForCountry != null) {
            showComponent(adminAreaSection);
            showComponent(adminAreaForCountry);
        } else {
            // 6. The country selected has no admin area selector, so hide the whole section
            const adminAreaReveal =
                document.getElementById("admin-area-reveal");
            if (selectedAdminAreasIds.length > 0) {
                adminAreaReveal.setAttribute("checked", "");
            }
            hideComponent(adminAreaSection);
        }
    };

    // Get all admin-area selector buttons
    const addAdminAreaButtons = document.querySelectorAll(
        "#admin-area-choices-button"
    );
    // Loop through each and add event listener to build admin areas list
    addAdminAreaButtons.forEach(function (currentAddAdminButton) {
        currentAddAdminButton.addEventListener("click", function () {
            // Get the selector element for the selected country
            const adminAreaSelector = document.getElementById(
                currentAddAdminButton.getAttribute("name")
            );

            // Append selected value to hidden input list
            const adminAreasInput = document.getElementById(
                "admin-areas-selection-input"
            );

            // Only continue if selected value is not 'choose your location'
            if (adminAreaSelector.value != 0) {
                // If the admin area is not in the selected array, push it there and update
                // the hidden submission value
                if (!selectedAdminAreasIds.includes(adminAreaSelector.value)) {
                    selectedAdminAreasIds.push(adminAreaSelector.value);
                }
                adminAreasInput.value = selectedAdminAreasIds;

                // Add selected admin area to admin area list
                var selectedAdminAreaName =
                    adminAreaSelector.options[adminAreaSelector.selectedIndex]
                        .text;
                if (!selectedAdminAreasNames.includes(selectedAdminAreaName)) {
                    // Only add name to list if it isn't already present
                    selectedAdminAreasNames.push(selectedAdminAreaName);
                }
                updateSelectedAdminAreasContainer(
                    selectedAdminAreasNames,
                    selectedAdminAreasIds
                );
            }
        });
    });

    // Function called which will update the Admin Areas selection list box based
    // on a given list of admin areas
    const updateSelectedAdminAreasContainer = function (
        adminAreasList,
        adminAreasIds
    ) {
        const adminAreasSelectedBox = document.getElementById(
            "selected-admin-areas-container"
        );
        if (adminAreasList == "") {
            hideComponent(adminAreasSelectedBox);
        } else {
            showComponent(adminAreasSelectedBox);

            // 1. Clear the admin area list box
            const adminAreaSelectList =
                document.getElementById("selection-list");
            adminAreaSelectList.innerHTML = "";

            // 2. Build the admin areas display HTML box and add to display
            for (var x = 0; x < adminAreasList.length; x++) {
                // List item element
                const listItem = document.createElement("li");
                listItem.classList.add("selection-list__list__item");
                adminAreaSelectList.appendChild(listItem);
                // List item number and name
                const spanItem = document.createElement("span");
                spanItem.classList.add("selection-list__list__item__number");
                spanItem.setAttribute("data-number", x + 1);
                listItem.appendChild(spanItem);
                listItem.innerHTML = listItem.innerHTML.concat(
                    adminAreasList[x]
                );
                // Remove item section
                const removeItemDiv = document.createElement("div");
                removeItemDiv.classList.add(
                    "selection-list__list__item__remove-form"
                );
                listItem.appendChild(removeItemDiv);
                // Remove item button
                const removeItemButton = document.createElement("div");
                removeItemButton.classList.add(
                    "selection-list__list__item__remove-form__submit"
                );
                removeItemButton.innerHTML = "Remove";
                removeItemButton.setAttribute("id", "remove-button");
                removeItemButton.setAttribute("name", adminAreasList[x]);
                removeItemButton.setAttribute("value", adminAreasIds[x]);
                removeItemDiv.appendChild(removeItemButton);
            }

            // 3. Get all remove buttons
            const removeAdminAreaButtons =
                document.querySelectorAll("#remove-button");
            // 4. Setup functionality for when a remove button is clicked
            removeAdminAreaButtons.forEach(function (currentRemoveAdminButton) {
                currentRemoveAdminButton.addEventListener("click", function () {
                    // Get the name & id of the admin area you are attempting to remove
                    removeAdminId =
                        currentRemoveAdminButton.getAttribute("value");
                    removeAdminName =
                        currentRemoveAdminButton.getAttribute("name");
                    // Find the index in the array which holds the name of the admin area
                    const nameIndex =
                        selectedAdminAreasNames.indexOf(removeAdminName);
                    // Remove the name from the array
                    selectedAdminAreasNames.splice(nameIndex, 1);
                    // Find the index in the array which holds the id of the admin area
                    const idIndex =
                        selectedAdminAreasIds.indexOf(removeAdminId);
                    // Remove the id from the array
                    selectedAdminAreasIds.splice(idIndex, 1);
                    // Remove id from hidden input
                    const adminAreasInput = document.getElementById(
                        "admin-areas-selection-input"
                    );
                    adminAreasInput.value = selectedAdminAreasIds;
                    // Re-render the admin area container
                    updateSelectedAdminAreasContainer(
                        selectedAdminAreasNames,
                        selectedAdminAreasIds
                    );
                });
            });
        }
    };
};
