const monthInputID = "status-date-group-estimated_resolution_date_0";
const yearInputID = "status-date-group-estimated_resolution_date_1";
const erdRequiredApprovalWarningID = "erd-requires-approval-warning";

const getMonthValue = () => {
    const monthInput = document.getElementById(monthInputID);
    return monthInput.value;
};

const getYearValue = () => {
    const yearInput = document.getElementById(yearInputID);
    return yearInput.value;
};

ma.components.setupHiddenERDTextarea = function (props) {
    const { isAdmin, proposedDate } = props;
    if (isAdmin === "True") {
        // if user is admin, don't run this code
        return;
    }
    const proposedDateObject = new Date(proposedDate);

    let monthInput = document.getElementById(monthInputID);
    let yearInput = document.getElementById(yearInputID);
    const erdWarning = document.getElementById(erdRequiredApprovalWarningID);
    const textarea = document.getElementById(
        "estimated_resolution_date_change_reason-form-group"
    );
    const editErdButton = document.getElementById("edit-erd-link");

    // if user clicks edit button, show textarea
    editErdButton?.addEventListener("click", () => {
        textarea.style.display = "block";
        // set month and year inputs to proposed date
        monthInput.value = proposedDateObject.getMonth();
        yearInput.value = proposedDateObject.getFullYear();
    });

    const referenceMonth = getMonthValue();
    const referenceYear = getYearValue();

    // if month and year are empty, exit early
    if (!referenceMonth || !referenceYear) {
        return;
    }

    // use
    const referenceDate = new Date(referenceYear, referenceMonth, 1);
    console.log("referenceDate", referenceDate);

    const updateTextarea = () => {
        const currentMonth = getMonthValue();
        const currentYear = getYearValue();
        const currentDate = new Date(currentYear, currentMonth, 1);
        // if date is later than reference date, show textarea otherwise hide it
        if (currentDate > referenceDate) {
            textarea.style.display = "block";
            erdWarning.style.display = "block";
        } else {
            textarea.style.display = "none";
            erdWarning.style.display = "none";
        }
    };

    monthInput.addEventListener("change", updateTextarea);
    yearInput.addEventListener("change", updateTextarea);
};
