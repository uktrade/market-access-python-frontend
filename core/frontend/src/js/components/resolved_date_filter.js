// Establish resolved_date checkboxes and filter inputs and event listeners to hide/unhide sections
const open_pending_action_checkbox = document.getElementById("status-1");
let open_pending_action_date_filter = document.getElementById(
    "resolved_date_filter_open_pending_action"
);
open_pending_action_checkbox.addEventListener("change", (event) => {
    if (event.currentTarget.checked) {
        showDateFilter(open_pending_action_date_filter);
    } else {
        hideDateFilter(open_pending_action_date_filter);
        clearDateFilter(1);
    }
});

const open_in_progress_checkbox = document.getElementById("status-2");
let open_in_progress_date_filter = document.getElementById(
    "resolved_date_filter_open_in_progress"
);
open_in_progress_checkbox.addEventListener("change", (event) => {
    if (event.currentTarget.checked) {
        showDateFilter(open_in_progress_date_filter);
    } else {
        hideDateFilter(open_in_progress_date_filter);
        clearDateFilter(2);
    }
});

const resolved_in_part_checkbox = document.getElementById("status-3");
let resolved_in_part_date_filter = document.getElementById(
    "resolved_date_filter_resolved_in_part"
);
resolved_in_part_checkbox.addEventListener("change", (event) => {
    if (event.currentTarget.checked) {
        showDateFilter(resolved_in_part_date_filter);
    } else {
        hideDateFilter(resolved_in_part_date_filter);
        clearDateFilter(3);
    }
});

const resolved_in_full_checkbox = document.getElementById("status-4");
let resolved_in_full_date_filter = document.getElementById(
    "resolved_date_filter_resolved_in_full"
);
resolved_in_full_checkbox.addEventListener("change", (event) => {
    if (event.currentTarget.checked) {
        showDateFilter(resolved_in_full_date_filter);
    } else {
        hideDateFilter(resolved_in_full_date_filter);
        clearDateFilter(4);
    }
});

function showDateFilter(date_filter) {
    date_filter.removeAttribute("hidden");
}

function hideDateFilter(date_filter) {
    date_filter.setAttribute("hidden", true);
}

function clearDateFilter(status_id) {
    document.getElementById(`resolved_date_from_month_${status_id}`).value = "";
    document.getElementById(`resolved_date_from_year_${status_id}`).value = "";
    document.getElementById(`resolved_date_to_month_${status_id}`).value = "";
    document.getElementById(`resolved_date_to_month_${status_id}`).value = "";
}
