ma.pages.topBarrierPriority = {
    topPriorityVisiblity: function (
        top_priority_status,
        existing_top_priority_summary
    ) {
        // Collect HTML components
        // Section which will ask either for admins to approve a barrier top priority change, or anyone to request a change
        const topPriorityConsiderationContainer =
            document.getElementById("top_barrier");

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
        const regionalRadioInput = document.getElementById("priority_level-1");
        const countryRadioInput = document.getElementById("priority_level-2");
        const watchlistRadioInput = document.getElementById("priority_level-3");

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
        hideComponent(topPriorityConsiderationContainer);
        hideComponent(topPriorityNotice);
        hideComponent(topPriorityWatchlistWarning);
        hideComponent(topPrioritySummaryDescriptionContainer);
        hideComponent(topPrioritySummaryDescriptionInput);
        hideComponent(topPrioritySummaryExistingText);
        hideComponent(topPrioritySummaryHintText);
        hideComponent(topPrioritySummaryDates);
        hideComponent(topPriorityRejectionDescriptionContainer);

        // If any of the situations are true, we need to display the consider Top Priority question
        // - Country or regional priority levels selected already
        // - Barrier is already Top Priority
        if (
            regionalRadioInput.checked == true ||
            countryRadioInput.checked == true ||
            top_priority_status == "APPROVAL_PENDING" ||
            top_priority_status == "REMOVAL_PENDING" ||
            top_priority_status == "APPROVED"
        ) {
            showComponent(topPriorityConsiderationContainer);
        }

        // If the page has defaulted to watchlist with a Top Priority status (such as an error message triggering)
        // Need to display watchlist/top priority warning
        if (
            watchlistRadioInput.checked == true &&
            (top_priority_status == "APPROVAL_PENDING" ||
                top_priority_status == "REMOVAL_PENDING" ||
                top_priority_status == "APPROVED")
        ) {
            showComponent(topPriorityWatchlistWarning);
        }

        // If we reload the page with a Top Priority barrier and watchlist selected
        // Need to hide the consideration question
        if (
            watchlistRadioInput.checked == true &&
            top_priority_status == "APPROVED"
        ) {
            hideComponent(topPriorityConsiderationContainer);
        }

        // If any of the following situations are true, we need to display the priority notice
        // - If barrier is awaiting change approval
        if (
            top_priority_status == "APPROVAL_PENDING" ||
            top_priority_status == "REMOVAL_PENDING"
        ) {
            showComponent(topPriorityNotice);
        }

        // If any of the following situations are true, we need to display the priority summary section and its contents
        // - If barrier is already a top priority barrier and no is selected for top priority confirmation
        if (
            top_priority_status == "APPROVED" &&
            topPriorityConsiderationNoRadio.checked == true
        ) {
            showComponent(topPrioritySummaryDescriptionContainer);
            showComponent(topPrioritySummaryDescriptionInput);
        }

        // If any of the following situations are true, we need to display the editable priority summary section
        // - If barrier is awaiting approval, show the summary section so it can be edited
        if (
            top_priority_status == "APPROVAL_PENDING" ||
            top_priority_status == "APPROVED" ||
            top_priority_status == "REMOVAL_PENDING"
        ) {
            showComponent(topPrioritySummaryDescriptionContainer);
            showComponent(topPrioritySummaryExistingText);
            showComponent(topPrioritySummaryDates);
            // Additionally, barriers with a removal pending need updated text label
            if (top_priority_status == "REMOVAL_PENDING") {
                topPrioritySummaryInputLabel.innerHTML =
                    "Describe why this should be removed as a top 100 priority barrier";
            }
        }

        // Set event listeners.
        // The priority radio buttons
        // - Regional and Country buttons show the consider top priority question
        // - Watchlist button hides top priority question, sets it to 'no' and hides the description UNLESS we have a top priority status already
        regionalRadioInput.addEventListener("change", function () {
            showComponent(topPriorityConsiderationContainer);
            hideComponent(topPriorityWatchlistWarning);
        });
        countryRadioInput.addEventListener("change", function () {
            showComponent(topPriorityConsiderationContainer);
            hideComponent(topPriorityWatchlistWarning);
        });
        watchlistRadioInput.addEventListener("change", function () {
            if (
                top_priority_status == "" ||
                top_priority_status == "NONE" ||
                top_priority_status == "RESOLVED"
            ) {
                topPriorityConsiderationYesRadio.checked = false;
                topPriorityConsiderationNoRadio.checked = true;
                hideComponent(topPriorityConsiderationContainer);
                hideComponent(topPriorityNotice);
                hideComponent(topPrioritySummaryDescriptionContainer);
                hideComponent(topPriorityRejectionDescriptionContainer);
            } else if (top_priority_status == "APPROVED") {
                topPriorityConsiderationYesRadio.checked = false;
                topPriorityConsiderationNoRadio.checked = true;
                hideComponent(topPriorityConsiderationContainer);
                showComponent(topPriorityWatchlistWarning);
                showComponent(topPrioritySummaryDescriptionContainer);
            } else {
                showComponent(topPriorityWatchlistWarning);
            }
        });

        // The consider top priority question radio buttons - not present if top_priority
        if (topPriorityConsiderationYesRadio != null) {
            topPriorityConsiderationYesRadio.addEventListener(
                "change",
                function () {
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
