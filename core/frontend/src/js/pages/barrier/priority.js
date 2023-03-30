ma.pages.barrier.priority = {
    priorityFormReveal: function (top_priority_status) {
        const confirmPrioritySection = document.getElementById(
            "confirm-priority-form-section"
        );
        const confirmPriorityButton = document.getElementById(
            "confirm-priority-button"
        );
        const confirmPriorityButtonJs = document.getElementById(
            "confirm-priority-button-js"
        );
        const errorBanner = document.getElementById("add-priority-errors");
        const isUserAdmin =
            document.getElementById("is_user_admin").value == "True";

        const priorityRejectionForm = document.getElementById(
            "priority-rejection-form"
        );
        const priorityRejectionSummaryForm = document.getElementById(
            "priority_summary-rejection"
        );

        const showYesNo =
            top_priority_status == "APPROVED" || top_priority_status == "NONE";

        const priorityForm = document.getElementById("priority-form");
        // if container doesn't exist, return
        if (!confirmPrioritySection) {
            return;
        }
        if (showYesNo) {
            priorityForm.style = "display: none";
            confirmPrioritySection.style = "display: block";
        } else {
            priorityForm.style = "display: block";
            confirmPrioritySection.style = "display: none";
        }
        // Hide non-js button, display JS enabled button
        confirmPriorityButton.style = "display: none";
        confirmPriorityButtonJs.style = "display: inline-block";

        const handleInitialAnswerSubmission = function () {
            const yesRadioInput = document.getElementById(
                "confirm-priority-yes"
            );
            const noRadioInput = document.getElementById("confirm-priority-no");
            if (yesRadioInput.checked == true) {
                // Yes selected, show form proper, hide initial question
                priorityForm.style = "display: block";
                confirmPrioritySection.style = "display: none";
                // Ensure error for initial form is not visible
                errorBanner.style = "display: none";
            } else if (noRadioInput.checked == true) {
                // No selected, redirect back to barrier page, copy behaviour of cancel button
                if (isUserAdmin) {
                    window.location.href = "?confirm-priority=no";
                } else {
                    if (top_priority_status == "APPROVED") {
                        confirmPrioritySection.style = "display: none";
                        priorityRejectionForm.style = "display: block";
                        priorityRejectionSummaryForm.style = "display: block";
                    } else {
                        window.location.href = "?confirm-priority=no";
                    }
                }
            } else {
                // make error appear
                const errorText = document.getElementById(
                    "confirm-priority-error"
                );
                errorBanner.style = "display: inline-block";
                errorText.style = "display: inline-block";
            }
        };

        // add event listener to top barrier status
        confirmPriorityButtonJs.addEventListener("click", function () {
            handleInitialAnswerSubmission();
        });
    },
};
