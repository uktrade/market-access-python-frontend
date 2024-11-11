ma.components.MultiSelect = function (element) {
    const nodes = document.getElementById(element)

    const select = document.getElementById("dropdown");
    const add_button = document.getElementById("add_button");
    const display_list = document.getElementById("list_display");
    const selection = document.getElementById("id_form");
    
    add_button.addEventListener("click", function () {
        if (select.value) {
            additionMode();
        }
    });
    const additionMode = function () {
        appendToList();
    };

    const appendToList = function () {
        if (selection.value) {
            const new_list = JSON.parse(selection.value).map(function (e) {
                return e.toString();
            });
            if (!new_list.includes(select.value)) {
                new_list.push(select.value);
                selection.value = JSON.stringify(new_list);
            }
        } else {
            const new_list = [];
            new_list.push(select.value);
            selection.value = JSON.stringify(new_list);
        }

        updateDisplay();
    };

    const updateDisplay = function () {
        if (selection.value) {
            const selected_list = JSON.parse(selection.value).map(function (e) {
                return e.toString();
            });
            display_list.innerHTML = "";
            for (let i = 0; i < selected_list.length; i++) {
                for (let x = 0; x < select.length; x++) {
                    let option = select.options[x];
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
        if (selection.value) {
            let selected_list = JSON.parse(selection.value).map(function (e) {
                return e.toString();
            });
            const index = selected_list.indexOf(item);
            if (index > -1) {
                // only splice array when item is found
                selected_list.splice(index, 1);
            }
            selection.value = JSON.stringify(selected_list);
            updateDisplay();
        }
    };

    updateDisplay();
};
