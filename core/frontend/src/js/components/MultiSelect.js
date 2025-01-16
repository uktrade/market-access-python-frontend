ma.components.MultiSelect = function (/** @type {string} */ id_name) {
    const nodes = document.getElementById(id_name);

    const select = nodes.querySelector(".dropdown");
    const add_button = nodes.querySelector(".add_button");
    const display_list = nodes.querySelector(".list_display");
    const selection = nodes
        .querySelector(".input_form")
        .querySelectorAll("input")[1];

    add_button.addEventListener("click", function () {
        // @ts-ignore
        if (select.value) {
            additionMode();
        }
    });
    const additionMode = function () {
        appendToList();
    };

    const appendToList = function () {
        if (selection.value) {
            const new_list = JSON.parse(selection.value).map(
                function (/** @type {{ toString: () => any; }} */ e) {
                    return e.toString();
                },
            );
            // @ts-ignore
            if (!new_list.includes(select.value)) {
                // @ts-ignore
                new_list.push(select.value);
                selection.value = JSON.stringify(new_list);
            }
        } else {
            const new_list = [];
            // @ts-ignore
            new_list.push(select.value);
            selection.value = JSON.stringify(new_list);
        }

        updateDisplay();
    };

    const updateDisplay = function () {
        if (selection.value) {
            const selected_list = JSON.parse(selection.value).map(
                function (/** @type {{ toString: () => any; }} */ e) {
                    return e.toString();
                },
            );
            display_list.innerHTML = "";
            for (let i = 0; i < selected_list.length; i++) {
                // @ts-ignore
                for (let x = 0; x < select.length; x++) {
                    // @ts-ignore
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

    const removeItem = function (/** @type {any} */ item) {
        if (selection.value) {
            let selected_list = JSON.parse(selection.value).map(
                function (/** @type {{ toString: () => any; }} */ e) {
                    return e.toString();
                },
            );
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
