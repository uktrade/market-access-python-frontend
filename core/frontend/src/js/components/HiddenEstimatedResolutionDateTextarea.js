const defaultMonthInputID = "status-date-group-estimated_resolution_date_0";
const defaultYearInputID = "status-date-group-estimated_resolution_date_1";
const erdRequiredApprovalWarningID = "erd-requires-approval-warning";

const getMonthValue = (monthInputID) => {
    const monthInput = document.getElementById(monthInputID);
    return monthInput.value;
};

const getYearValue = (yearInputID) => {
    const yearInput = document.getElementById(yearInputID);
    return yearInput.value;
};

ma.components.setupHiddenERDTextarea = function (props) {
    //let [isAdmin, proposedDate, monthInputID, yearInputID] = props;
    console.log("Props ", props);
    console.log("Is user admin?: ", props.is_admin);
    console.log("input month", props.monthInput);
    if (props.is_admin == "True") {
        // if user is admin, don't run this code
        console.log("User is an admin, exit prompt");
        return;
    }
    if (typeof props.monthInput == "undefined") {
        monthInputID = defaultMonthInputID;
    }
    if (typeof props.yearInput == "undefined") {
        yearInputID = defaultYearInputID;
    }
    const proposedDateObject = new Date(props.proposedDate);

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
        monthInput.value = proposedDateObject.getMonth() + 1;
        yearInput.value = proposedDateObject.getFullYear();
    });

    const referenceMonth = getMonthValue(monthInputID);
    const referenceYear = getYearValue(yearInputID);

    // if month and year are empty, exit early
    if (!referenceMonth || !referenceYear) {
        return;
    }

    // use
    const referenceDate = new Date(referenceYear, referenceMonth, 1);
    console.log("referenceDate", referenceDate);
    const formError = document.getElementById("error-summary-title");

    if (formError) {
        console.log("there is an error therefore display reason");
        textarea.style.display = "block";
        //erdWarning.style.display = "block";
    }

    const updateTextarea = () => {
        const currentMonth = getMonthValue(monthInputID);
        const currentYear = getYearValue(yearInputID);
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
