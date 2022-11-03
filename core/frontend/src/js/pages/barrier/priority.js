ma.pages.barrier.priority = {
    priorityFormReveal: function () {
        const confirmPrioritySection = document.getElementById(
            "confirm-priority-form-section"
        );
        const confirmPriorityButton = document.getElementById(
            "confirm-priority-button"
        );
        const confirmPriorityButtonJs = document.getElementById(
            "confirm-priority-button-js"
        );
        const errorBanner = document.getElementById(
            "add-priority-initial-question-error"
        );

        // if container doesn't exist, return
        if (!confirmPrioritySection) {
            return;
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
                const priorityForm = document.getElementById("priority-form");
                priorityForm.style = "display: block";
                confirmPrioritySection.style = "display: none";
                // Ensure error for initial form is not visible
                errorBanner.style = "display: none";
            } else if (noRadioInput.checked == true) {
                // No selected, redirect back to barrier page, copy behaviour of cancel button
                const cancelPriorityButton =
                    document.getElementById("cancel-priority");
                window.location.href = cancelPriorityButton.href;
            } else {
                // make error appear
                errorBanner.style = "display: inline-block";
            }
        };

        // add event listener to top barrier status
        confirmPriorityButtonJs.addEventListener("click", function () {
            handleInitialAnswerSubmission();
        });
    },
};
