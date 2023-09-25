ma.pages.topBarrierPriority = {
    topPriorityVisiblity: function (
        top_priority_status,
        existing_top_priority_summary
    ) {
        // Collect HTML components
        // Section which will ask either for admins to approve a barrier top priority change, or anyone to request a change
        const topPriorityConsiderationContainer =
            document.getElementById("top_barrier");

        const priorityLevelChoiceContainer =
            document.getElementById("priority_level");

        // Sections that contains the text box to let users add a summary justifying the top priority change
        const topPrioritySummaryDescriptionContainer = document.getElementById(
            "priority_summary-container"
        );
        const topPrioritySummaryInputLabel = document.getElementById(
            "priority-summary-input-label"
        );
        const topPriorityRejectionDescriptionContainer =
            document.getElementById("top_priority_rejection_summary-container");
        const topPrioritySummaryDescriptionInput =
            document.getElementById("priority_summary");
        const topPrioritySummaryEditButton = document.getElementById(
            "edit-priority-summary-button"
        );
        const topPrioritySummaryExistingText = document.getElementById(
            "priority-summary-existing"
        );
        const topPrioritySummaryHintText = document.getElementById(
            "priority-summary-hint"
        );
        const topPrioritySummaryDates = document.getElementById(
            "priority-summary-existing-dates"
        );

        // Notice for users regarding the process of top priority approval
        const topPriorityNotice = document.getElementById(
            "top-priority-request-notice"
        );
        const topPriorityWatchlistWarning = document.getElementById(
            "watchlist-warning-text"
        );

        // Radio buttons for the "Which priority type" question
        const top100RadioInput = document.getElementById("priority_level-1");
        const regionalRadioInput = document.getElementById("priority_level-2");
        const countryRadioInput = document.getElementById("priority_level-3");
        const watchlistRadioInput = document.getElementById("priority_level-4");

        // Yes/No radio buttons for the "Is this barrer considered a top priority" question
        const topPriorityConsiderationYesRadio =
            document.getElementById("top_barrier-1");
        const topPriorityConsiderationNoRadio =
            document.getElementById("top_barrier-2");

        // Button to submit form
        const submitButton = document.getElementById("submit-priority-form");

        // Functions to show/hide individual page componenets
        const showComponent = function (component) {
            if (component != null) {
                component.style = "display: block";
            }
        };
        const hideComponent = function (component) {
            if (component != null) {
                component.style = "display: none";
            }
        };

        // Functions to handle errors
        const showError = function () {
            // Get error elements
            const errorBanner = document.getElementById("add-priority-errors");
            const errorText = document.getElementById(
                "missing-description-error"
            );
            // Make error visible
            errorBanner.style = "display: inline-block";
            errorText.style = "display: inline-block";
            // Move user to top of form to see error message
            window.scrollTo(0, 0);
        };

        // Set initial visibility.

        // Hide all components and selectively reveal depending on barriers current priorities
        hideComponent(priorityLevelChoiceContainer);
        hideComponent(topPriorityConsiderationContainer);
        hideComponent(topPriorityNotice);
        hideComponent(topPriorityWatchlistWarning);
        hideComponent(topPrioritySummaryDescriptionContainer);
        hideComponent(topPrioritySummaryDescriptionInput);
        hideComponent(topPrioritySummaryExistingText);
        hideComponent(topPrioritySummaryHintText);
        hideComponent(topPrioritySummaryDates);
        hideComponent(topPriorityRejectionDescriptionContainer);

        if (
            top_priority_status == "" ||
            top_priority_status == "NONE" ||
            top_priority_status == "RESOLVED"
        ) {
            showComponent(priorityLevelChoiceContainer);
        }

        // If we have entered the page with Top100 radio checked, (such as in an error state)
        // we need to display extra PB100 summary question
        if (
            top100RadioInput.checked == true &&
            (top_priority_status == "" ||
                top_priority_status == "NONE" ||
                top_priority_status == "RESOLVED")
        ) {
            showComponent(topPriorityNotice);
            showComponent(topPrioritySummaryDescriptionContainer);
            showComponent(topPrioritySummaryHintText);
            showComponent(topPrioritySummaryDescriptionInput);
        }

        // If any of the following situations are true, we need to display the priority notice
        // - If barrier is awaiting change approval
        if (
            top_priority_status == "APPROVAL_PENDING" ||
            top_priority_status == "REMOVAL_PENDING"
        ) {
            showComponent(topPriorityNotice);
        }

        // If any of the following situations are true, we need to display the editable priority summary section
        // - If barrier is awaiting approval, show the summary section so it can be edited
        if (
            top_priority_status == "APPROVAL_PENDING" ||
            top_priority_status == "APPROVED" ||
            top_priority_status == "REMOVAL_PENDING"
        ) {
            showComponent(topPriorityConsiderationContainer);
            showComponent(topPrioritySummaryDescriptionContainer);
            showComponent(topPrioritySummaryExistingText);
            showComponent(topPrioritySummaryDates);
            // Additionally, barriers with a removal pending need updated text label
            if (
                top_priority_status == "REMOVAL_PENDING" &&
                topPrioritySummaryInputLabel !== null
            ) {
                topPrioritySummaryInputLabel.innerHTML =
                    "Describe why this should be removed as a top 100 priority barrier";
            }
        }

        // Set event listeners.
        // Selecting Top 100 radio will open up the top_priority_summary inputs
        top100RadioInput.addEventListener("change", function () {
            topPriorityConsiderationYesRadio.checked = true;
            hideComponent(topPriorityConsiderationContainer);
            hideComponent(topPriorityWatchlistWarning);

            if (top100RadioInput.checked == true) {
                if (
                    top_priority_status == "" ||
                    top_priority_status == "NONE" ||
                    top_priority_status == "RESOLVED"
                ) {
                    showComponent(topPriorityNotice);
                    showComponent(topPrioritySummaryDescriptionContainer);
                    showComponent(topPrioritySummaryHintText);
                    showComponent(topPrioritySummaryDescriptionInput);
                }
            }
        });
        regionalRadioInput.addEventListener("change", function () {
            lowLevelPriorityClickedEvent();
        });
        countryRadioInput.addEventListener("change", function () {
            lowLevelPriorityClickedEvent();
        });
        watchlistRadioInput.addEventListener("change", function () {
            lowLevelPriorityClickedEvent();
        });

        const lowLevelPriorityClickedEvent = function () {
            topPriorityConsiderationYesRadio.checked = false;
            topPriorityConsiderationNoRadio.checked = true;
            hideComponent(topPriorityConsiderationContainer);
            hideComponent(topPriorityNotice);
            hideComponent(topPrioritySummaryDescriptionContainer);
            hideComponent(topPriorityRejectionDescriptionContainer);
        };

        // The consider top priority question radio buttons - not present if top_priority
        if (topPriorityConsiderationYesRadio != null) {
            topPriorityConsiderationYesRadio.addEventListener(
                "change",
                function () {
                    if (
                        top_priority_status == "APPROVAL_PENDING" ||
                        top_priority_status == "REMOVAL_PENDING"
                    ) {
                        hideComponent(topPriorityRejectionDescriptionContainer);
                    }
                    if (top_priority_status == "APPROVED") {
                        showComponent(topPrioritySummaryDescriptionContainer);
                        hideComponent(topPrioritySummaryDescriptionInput);
                        showComponent(topPrioritySummaryHintText);
                        showComponent(topPrioritySummaryExistingText);
                        showComponent(topPrioritySummaryDates);
                        topPrioritySummaryInputLabel.innerHTML =
                            "Reason provided why this should be a potential top 100 barrier";
                        topPrioritySummaryDescriptionInput.value =
                            existing_top_priority_summary;
                    }
                }
            );
            topPriorityConsiderationNoRadio.addEventListener(
                "change",
                function () {
                    if (
                        top_priority_status == "" ||
                        top_priority_status == "NONE" ||
                        top_priority_status == "RESOLVED"
                    ) {
                        hideComponent(topPriorityNotice);
                        hideComponent(topPrioritySummaryHintText);
                        hideComponent(topPrioritySummaryDescriptionContainer);
                    }
                    if (
                        top_priority_status == "APPROVAL_PENDING" ||
                        top_priority_status == "REMOVAL_PENDING"
                    ) {
                        showComponent(topPriorityRejectionDescriptionContainer);
                    }
                    if (top_priority_status == "APPROVED") {
                        showComponent(topPrioritySummaryDescriptionContainer);
                        showComponent(topPrioritySummaryDescriptionInput);
                        showComponent(topPrioritySummaryHintText);
                        hideComponent(topPrioritySummaryExistingText);
                        hideComponent(topPrioritySummaryDates);
                        topPrioritySummaryInputLabel.innerHTML =
                            "Describe why this should be removed as a top 100 priority barrier";
                        topPrioritySummaryDescriptionInput.value = "";
                    }
                }
            );
        }

        // Clicking the edit button will show/hide the existing text and summary input area
        if (topPrioritySummaryEditButton != null) {
            topPrioritySummaryEditButton.addEventListener(
                "click",
                function (event) {
                    showComponent(topPrioritySummaryDescriptionInput);
                    hideComponent(topPrioritySummaryExistingText);
                    showComponent(topPrioritySummaryHintText);
                }
            );
        }

        // Check before submitting that summary is present, if required
        submitButton.addEventListener("click", function (event) {
            if (topPrioritySummaryDescriptionContainer != null) {
                const descriptionValue =
                    topPrioritySummaryDescriptionInput.value;
                if (
                    descriptionValue.length < 1 &&
                    topPriorityConsiderationYesRadio.checked == true &&
                    top_priority_status != "APPROVED"
                ) {
                    // Description is required when requesting top priority - ignore when
                    // the form is submitted for a barrier already in top priority status
                    // Stop button submitting
                    event.preventDefault();
                    // Show error box and scroll to top of page
                    showError();
                    // Add error focus bar to description section
                    descriptionSection.classList.add("govuk-form-group--error");
                }
            }

            if (topPriorityRejectionDescriptionContainer != null) {
                const rejectionValue = document.getElementById(
                    "top_priority_rejection_summary"
                ).value;
                if (
                    rejectionValue.length < 1 &&
                    topPriorityConsiderationNoRadio.checked == true
                ) {
                    // Stop button submitting
                    event.preventDefault();
                    // Show error box and scroll to top of page
                    showError();
                    // Add error focus bar to description section
                    topPriorityRejectionDescriptionContainer.classList.add(
                        "govuk-form-group--error"
                    );
                }
            }
        });
    },
};
