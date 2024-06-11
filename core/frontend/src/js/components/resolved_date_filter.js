// Establish resolved_date checkboxes and filter inputs and event listeners to hide/unhide sections
const open_in_progress_checkbox = document.getElementById("status-1");
let open_in_progress_date_filter = document.getElementById(
    "resolved_date_filter_open_in_progress"
);
open_in_progress_checkbox.addEventListener("change", (event) => {
    if (event.currentTarget.checked) {
        showDateFilter(open_in_progress_date_filter);
    } else {
        hideDateFilter(open_in_progress_date_filter);
        clearDateFilter("open_in_progress");
    }
});

const resolved_in_part_checkbox = document.getElementById("status-2");
let resolved_in_part_date_filter = document.getElementById(
    "resolved_date_filter_resolved_in_part"
);
resolved_in_part_checkbox.addEventListener("change", (event) => {
    if (event.currentTarget.checked) {
        showDateFilter(resolved_in_part_date_filter);
    } else {
        hideDateFilter(resolved_in_part_date_filter);
        clearDateFilter("resolved_in_part");
    }
});

const resolved_in_full_checkbox = document.getElementById("status-3");
let resolved_in_full_date_filter = document.getElementById(
    "resolved_date_filter_resolved_in_full"
);
resolved_in_full_checkbox.addEventListener("change", (event) => {
    if (event.currentTarget.checked) {
        showDateFilter(resolved_in_full_date_filter);
    } else {
        hideDateFilter(resolved_in_full_date_filter);
        clearDateFilter("resolved_in_full");
    }
});

function showDateFilter(date_filter) {
    date_filter.removeAttribute("hidden");
}

function hideDateFilter(date_filter) {
    date_filter.setAttribute("hidden", true);
}

function clearDateFilter(status) {
    for (const item of document.querySelectorAll(
        `input[name^="status_date_${status}"]`
    )) {
        item.value = "";
    }
}
