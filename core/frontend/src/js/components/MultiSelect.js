ma.components.MultiSelect = function (category) {
    
    const add_button = document.getElementById("add_button");
    const dropdown = document.getElementById(category + "_select");
    let current_list_element = document.getElementById("id_" + category + "s")

    add_button.addEventListener("click", function () {
        additionMode();
    });
    const additionMode = function () {
        appendToList();
    };

    const appendToList = function () {
        if (current_list_element.value) {
            const new_list = JSON.parse(current_list_element.value);
            if (!new_list.includes(dropdown.value)) {
                new_list.push(dropdown.value);
                current_list_element.value = JSON.stringify(new_list);
            }
        } else {
            const new_list = [];
            new_list.push(dropdown.value);
            current_list_element.value = JSON.stringify(new_list);
        }

        updateDisplay();
    };

    const updateDisplay = function () {
        const display_list = document.getElementById("list_display");

        if (current_list_element.value) {
            const selected_list = JSON.parse(current_list_element.value);
            display_list.innerHTML = "";
            for (let i = 0; i < selected_list.length; i++) {
                for (let x = 0; x < dropdown.length; x++) {
                    let option = dropdown.options[x];
                    if (option.value == selected_list[i]) {
                        let category_entry = document.createElement("li");
                        category_entry.classList.add(
                            "selection-list__list__item",
                        );
                        category_entry.appendChild(
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
                        category_entry.appendChild(remove_link);
                        display_list.appendChild(category_entry);
                    }
                }
            }
        }
    };

    const removeItem = function (item) {
        if (current_list_element.value) {
            let selected_list = JSON.parse(current_list_element.value);
            const index = selected_list.indexOf(item);
            if (index > -1) {
                // only splice array when item is found
                selected_list.splice(index, 1);
            }
            current_list_element.value = JSON.stringify(selected_list);
            updateDisplay();
        }
    };

    updateDisplay();
};
