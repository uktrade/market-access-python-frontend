const defaultMonthInputID = "status-date-group-estimated_resolution_date_0";
const defaultYearInputID = "status-date-group-estimated_resolution_date_1";
const erdRequiredApprovalWarningID = "erd-requires-approval-warning";
const erdChangeReason = document.getElementById("estimated_resolution_date_change_reason")


const getMonthValue = (monthInputID) => {
    const monthInput = document.getElementById(monthInputID);
    return monthInput.value;
};

const getYearValue = (yearInputID) => {
    const yearInput = document.getElementById(yearInputID);
    return yearInput.value;
};

ma.components.setupHiddenERDTextarea = function (props) {
    console.log("Checking hidden reason text");

    const proposedDateObject = new Date(props.proposedDate);

    if (typeof props.monthInput == "undefined") {
        monthInputID = defaultMonthInputID;
    }
    if (typeof props.yearInput == "undefined") {
        yearInputID = defaultYearInputID;
    }

    let monthInput = document.getElementById(monthInputID);
    let yearInput = document.getElementById(yearInputID);
    const erdWarning = document.getElementById(erdRequiredApprovalWarningID);
    const textarea = document.getElementById(
        "estimated_resolution_date_change_reason-form-group"
    );
    const editErdButton = document.getElementById("edit-erd-link");
    const referenceMonth = getMonthValue(monthInputID);
    const referenceYear = getYearValue(yearInputID);

    console.log("reference date", referenceMonth, referenceYear)

    if (props.is_admin == "True" && (referenceMonth && referenceYear)) {
        // if user is admin and not clearing erd, don't run this code
        console.log("User is admin exiting")
        return;
    }



    // if user clicks edit button, show textarea
    editErdButton?.addEventListener("click", () => {
        textarea.style.display = "block";
        // set month and year inputs to proposed date
        monthInput.value = proposedDateObject.getMonth() + 1;
        yearInput.value = proposedDateObject.getFullYear();
    });

    console.log("button watch init")



    // if month and year are empty, exit early
    if (!(props.is_admin == "True") && (!referenceMonth && !referenceYear)) {
        console.log("Exiting because reference date is empty")
        return;
    }

    // use
    const referenceDate = new Date(referenceYear, referenceMonth, 1);
    const formError = document.getElementById("error-summary-title");
    console.log("Form Error:");
    console.log(formError);

    if (formError) {
        console.log("Form error therefore display ERD reason");
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
            console.log("current date not equal to proposed date")
        }
        else if (erdChangeReason.value) {
            textarea.style.display = "block";
            erdWarning.style.display = "block";
            console.log("there is an existing reason so display it", erdChangeReason.value)
        }
        else {
            textarea.style.display = "none";
            erdWarning.style.display = "none";
        }
    };

    monthInput.addEventListener("change", updateTextarea);
    yearInput.addEventListener("change", updateTextarea);
};
