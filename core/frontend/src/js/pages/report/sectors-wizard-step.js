ma.pages.report.sectorsWizardStep = function () {
    // Get buttons from sections and assign them onclick events to call relevant function
    const addSectorButton = document.getElementById("add-other-sector-button");
    addSectorButton.addEventListener("click", function () {
        append_sector(
            "id_barrier-sectors-affected-sectors",
            "sectors_select",
            "sectors_list_display"
        );
    });
    const displayOtherSectorButton = document.getElementById(
        "display-other-sector-button"
    );
    displayOtherSectorButton.addEventListener("click", function () {
        toggle_mode("edit");
    });

    const toggle_mode = function (mode) {
        // Function that switches display between 'edit' and 'display'
        // 'display' = box listing all selected sectors is visible
        // 'edit' = box where you can select and add sector is visible
        const edit_div = document.getElementById("sectors_edit");
        const display_div = document.getElementById("sectors_display");

        if (mode === "edit") {
            // Toggling to edit mode
            edit_div.style.display = "block";
            display_div.style.display = "none";
        } else {
            // Toggling to display mode
            display_div.style.display = "block";
            edit_div.style.display = "none";

            // Hide or show the list of sectors depending if we have any selected
            const sectorsList = document.getElementById("sectors_list_display");
            let current_sector_list = document.getElementById(
                "id_barrier-sectors-affected-sectors"
            );
            if (current_sector_list.value === "") {
                sectorsList.style.display = "none";
            } else {
                sectorsList.style.display = "block";
            }
        }
    };

    const append_sector = function (fieldname, select, display_list) {
        let sector_select = document.getElementById(select);
        let sector = sector_select.value;
        //let sector_name = sector_select.options[sector_select.selectedIndex].text;
        let current_sector_list = document.getElementById(fieldname);

        if (current_sector_list.value) {
            // Current sector hidden input has value
            // Parse the existing list so we can add to it
            const new_list = JSON.parse(current_sector_list.value);
            if (!new_list.includes(sector)) {
                // Sector ID not in hidden input list, so add this to the list
                new_list.push(sector);
                // Update the hidden input value with the updated list
                current_sector_list.value = JSON.stringify(new_list);
            }
        } else {
            // Current sector hidden input empty
            // Create empty list
            const new_list = [];
            // Push sector ID into list
            if (sector) {
                new_list.push(sector);
            }
            // Set hidden input value to contain the list
            current_sector_list.value = JSON.stringify(new_list);
        }

        // Update the display box with the new updated list
        update_sector_display();
        // Toggle back to display mode
        toggle_mode("display");
    };

    const update_sector_display = function () {
        const sector_list = document.getElementById("sectors_select");
        const current_selected_list = document.getElementById(
            "id_barrier-sectors-affected-sectors"
        );
        const display_list = document.getElementById("sectors_list_display");
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
                            "selection-list__list__item"
                        );
                        sector_entry.appendChild(
                            document.createTextNode(option.text)
                        );
                        let remove_link = document.createElement("a");
                        let remove_link_text =
                            document.createTextNode("remove");
                        remove_link.setAttribute("href", "#");
                        remove_link.addEventListener("click", function () {
                            remove_item(option.value);
                        });
                        remove_link.appendChild(remove_link_text);
                        remove_link.classList.add(
                            "selection-list__list__item__remove-form"
                        );
                        sector_entry.appendChild(remove_link);
                        display_list.appendChild(sector_entry);
                    }
                }
            }
        }
    };

    const remove_item = function (item) {
        const current_selected_list = document.getElementById(
            "id_barrier-sectors-affected-sectors"
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
            update_sector_display();
        }
    };

    // Set initial visibility mode & initial list of selected sectors
    toggle_mode("display");
    update_sector_display();
};
