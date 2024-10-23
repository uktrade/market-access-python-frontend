ma.components.MultiSelect = function (category, main_and_other=false) {
    // Get buttons from sections and assign them onclick events to call relevant function
    if (main_and_other === true) {
        const mainCategorySelect = document.getElementById("main_" + category + "_select");
        var currentMainCategorySelected = mainCategorySelect.value;
        mainCategorySelect.addEventListener("change", function () {
            updateOtherCategoriesList(mainCategorySelect.value);
            removeItem(mainCategorySelect.value);
        });
    }
    
    const addButton = document.getElementById("add_button");
    addButton.addEventListener("click", function () {
        additionMode();
    });
    const select = document.getElementById(category + "_select");

    const additionMode = function () {
        if (select.style.display == "none") {
            select.style.display = "block";
        } else {
            appendCategory(
                "selected_sectors",
                category + "_select",
                category + "_list_display",
            );
            select.style.display = "none";
        }
    };


    const appendCategory = function (fieldname, select, display_list) {
        let category_select = document.getElementById(select);
        let category = category_select.value;
        let current_category_list = document.getElementById(fieldname).getElementsByTagName('input')[0];

        if (current_category_list.value) {
            // Current sector hidden input has value
            // Parse the existing list so we can add to it
            const new_list = JSON.parse(current_category_list.value);
            if (!new_list.includes(category)) {
                // Sector ID not in hidden input list, so add this to the list
                new_list.push(category);
                // Update the hidden input value with the updated list
                current_category_list.value = JSON.stringify(new_list);
            }
        } else {
            // Current sector hidden input empty
            // Create empty list
            const new_list = [];
            // Push sector ID into list
            if (category) {
                category.push(category);
            }
            // Set hidden input value to contain the list
            current_category_list.value = JSON.stringify(new_list);
        }

        // Update the display box with the new updated list
        updateDisplay();
    };

    const updateDisplay = function () {
        const sector_list = document.getElementById(category + "_select");
        const current_selected_list = document.getElementById(
            "id_barrier-sectors-affected-sectors",
        );
        const display_list = document.getElementById(category + "_list_display");

        if (current_selected_list.value == "") {
            const selected_list = current_selected_list.value;
        } else {
            const selected_list = JSON.parse(current_selected_list.value);
            display_list.innerHTML = "";
            for (let i = 0; i < selected_list.length; i++) {
                for (let x = 0; x < sector_list.length; x++) {
                    let option = sector_list.options[x];
                    if (option.value == selected_list[i]) {
                        let sector_entry = document.createElement("li");
                        sector_entry.classList.add(
                            "selection-list__list__item",
                        );
                        sector_entry.appendChild(
                            document.createTextNode(option.text),
                        );
                        // Add remove link to each sector
                        let remove_link = document.createElement("button");
                        let remove_link_text =
                            document.createTextNode("remove");
                        remove_link.setAttribute("type", "button");
                        remove_link.setAttribute(
                            "aria-label",
                            `remove ${option.innerHTML}`,
                        );
                        remove_link.addEventListener("click", function () {
                            removeItem(option.value);
                        });
                        remove_link.appendChild(remove_link_text);
                        remove_link.classList.add(
                            "selection-list__list__item__remove-form__submit",
                        );
                        sector_entry.appendChild(remove_link);
                        display_list.appendChild(sector_entry);
                    }
                }
            }
        }
    };

    const updateOtherCategoriesList = function (sector) {
        // Want to prevent item selected as main sector to be available as an option for other sector
        if (sector != "") {
            // Hide newly selected option in the other sectors selection box
            otherSectorItemElementName = "other-sectors-select-".concat(sector);
            const otherSectorItem = document.getElementById(
                otherSectorItemElementName,
            );
            otherSectorItem.style.display = "none";
            // Show previously selected option in the other sectors selection box
            if (
                currentMainCategorySelected != sector &&
                currentMainCategorySelected != ""
            ) {
                previousSectorItemElementName = "other-sectors-select-".concat(
                    currentMainCategorySelected,
                );
                console.log(previousSectorItemElementName);
                const previousSectorItem = document.getElementById(
                    previousSectorItemElementName,
                );
                previousSectorItem.style.display = "block";
            }
            // Set variable tracking selected sector to the new value
            currentMainCategorySelected = sector;
        }
    };

    const removeItem = function (item) {
        const current_selected_list = document.getElementById(
            "id_barrier-sectors-affected-sectors",
        );
        if (current_selected_list.value == "") {
            const selected_list = current_selected_list.value;
        } else {
            let selected_list = JSON.parse(current_selected_list.value);
            const index = selected_list.indexOf(item);
            if (index > -1) {
                // only splice array when item is found
                selected_list.splice(index, 1);
            }
            current_selected_list.value = JSON.stringify(selected_list);
            updateSectorDisplay();
        }
    };

    // Set initial visibility mode & initial list of selected sectors
    select.style.display = "none";
    updateOtherCategoriesList(currentMainCategorySelected);
    updateDisplay();
};
