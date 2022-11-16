ma.pages.topBarrierPriority = {
    topPriorityVisiblity: function (top_priority_status) {
        console.log("top priority status: " + top_priority_status);

        // Collect HTML components
        // Section which will ask either for admins to approve a barrier top priority change, or anyone to request a change
        const topPriorityConsiderationContainer =
            document.getElementById("top_barrier");

        // Sections that contains the text box to let users add a summary justifying the top priority change
        const topPrioritySummaryDescriptionContainer = document.getElementById(
            "priority_summary-container"
        );
        const topPriorityRejectionDescriptionContainer =
            document.getElementById("top_priority_rejection_summary-container");

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

        const rejectTopPriorityRequestRadio =
            document.getElementById("top_barrier-2");

        // Functions to show/hide individual page componenets
        const showConsiderationQuestion = function () {
            if (topPriorityConsiderationContainer != null) {
                topPriorityConsiderationContainer.style = "display: block";
            }
        };
        const hideConsiderationQuestion = function () {
            if (topPriorityConsiderationContainer != null) {
                topPriorityConsiderationContainer.style = "display: none";
            }
        };
        const showPriorityNotice = function () {
            if (topPriorityNotice != null) {
                topPriorityNotice.style = "display: block";
            }
        };
        const hidePriorityNotice = function () {
            if (topPriorityNotice != null) {
                topPriorityNotice.style = "display: none";
            }
        };
        const showPriorityWatchlistNotice = function () {
            if (topPriorityWatchlistWarning != null) {
                topPriorityWatchlistWarning.style = "display: block";
            }
        };
        const hidePriorityWatchlistNotice = function () {
            if (topPriorityWatchlistWarning != null) {
                topPriorityWatchlistWarning.style = "display: none";
            }
        };
        const showSummaryInput = function () {
            if (topPrioritySummaryDescriptionContainer != null) {
                topPrioritySummaryDescriptionContainer.style = "display: block";
            }
        };
        const hideSummaryInput = function () {
            if (topPrioritySummaryDescriptionContainer != null) {
                topPrioritySummaryDescriptionContainer.style = "display: none";
            }
        };
        const showRejectionInput = function () {
            if (topPriorityRejectionDescriptionContainer != null) {
                topPriorityRejectionDescriptionContainer.style =
                    "display: block";
            }
        };
        const hideRejectionInput = function () {
            if (topPriorityRejectionDescriptionContainer != null) {
                topPriorityRejectionDescriptionContainer.style =
                    "display: none";
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
        hideConsiderationQuestion();
        hidePriorityNotice();
        hidePriorityWatchlistNotice();
        hideSummaryInput();
        hideRejectionInput();
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
            showConsiderationQuestion();
        }

        // If the page has defaulted to watchlist with a Top Priority status (such as an error message triggering)
        // Need to display watchlist/top priority warning
        if (
            watchlistRadioInput.checked == true &&
            (top_priority_status == "APPROVAL_PENDING" ||
                top_priority_status == "REMOVAL_PENDING" ||
                top_priority_status == "APPROVED")
        ) {
            showPriorityWatchlistNotice();
        }

        // If we reload the page with a Top Priority barrier and watchlist selected
        // Need to hide the consideration question
        if (
            watchlistRadioInput.checked == true &&
            top_priority_status == "APPROVED"
        ) {
            hideConsiderationQuestion();
        }

        // If any of the following situations are true, we need to display the priority notice
        // - If barrier is awaiting change approval
        if (
            top_priority_status == "APPROVAL_PENDING" ||
            top_priority_status == "REMOVAL_PENDING"
        ) {
            showPriorityNotice();
        }

        // If any of the following situations are true, we need to display the priority summary
        // - If barrier is already a top priority barrier and no is selected for top priority confirmation
        if (
            top_priority_status == "APPROVED" &&
            topPriorityConsiderationNoRadio.checked == true
        ) {
            showSummaryInput();
        }

        // Set event listeners.
        // The priority radio buttons
        // - Regional and Country buttons show the consider top priority question
        // - Watchlist button hides top priority question, sets it to 'no' and hides the description UNLESS we have a top priority status already
        regionalRadioInput.addEventListener("change", function () {
            showConsiderationQuestion();
            hidePriorityWatchlistNotice();
        });
        countryRadioInput.addEventListener("change", function () {
            showConsiderationQuestion();
            hidePriorityWatchlistNotice();
        });
        watchlistRadioInput.addEventListener("change", function () {
            if (
                top_priority_status == "" ||
                top_priority_status == "NONE" ||
                top_priority_status == "RESOLVED"
            ) {
                topPriorityConsiderationYesRadio.checked = false;
                topPriorityConsiderationNoRadio.checked = true;
                hideConsiderationQuestion();
                hidePriorityNotice();
                hideSummaryInput();
                hideRejectionInput();
            } else if (top_priority_status == "APPROVED") {
                topPriorityConsiderationYesRadio.checked = false;
                topPriorityConsiderationNoRadio.checked = true;
                hideConsiderationQuestion();
                showPriorityWatchlistNotice();
                showSummaryInput();
            } else {
                showPriorityWatchlistNotice();
            }
        });

        if (rejectTopPriorityRequestRadio != null) {
            rejectTopPriorityRequestRadio.addEventListener(
                "change",
                function () {
                    const checked = rejectTopPriorityRequestRadio.checked;
                    console.log("rejection value", checked);
                    if (checked) {
                        showRejectionInput();
                    } else {
                        hideRejectionInput();
                    }
                }
            );
        }

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
                        showPriorityNotice();
                        showSummaryInput();
                    }
                    if (
                        top_priority_status == "APPROVAL_PENDING" ||
                        top_priority_status == "REMOVAL_PENDING"
                    ) {
                        hideRejectionInput();
                    }
                    if (top_priority_status == "APPROVED") {
                        hideSummaryInput();
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
                        hidePriorityNotice();
                        hideSummaryInput();
                    }
                    if (
                        top_priority_status == "APPROVAL_PENDING" ||
                        top_priority_status == "REMOVAL_PENDING"
                    ) {
                        showRejectionInput();
                    }
                    if (top_priority_status == "APPROVED") {
                        showSummaryInput();
                    }
                }
            );
        }

        // Check before submitting that summary is present, if required
        submitButton.addEventListener("click", function (event) {
            const descriptionSection = document.getElementById(
                "priority_summary-container"
            );
            const rejectionSection = document.getElementById(
                "top_priority_rejection_summary-container"
            );

            if (descriptionSection != null) {
                const descriptionValue =
                    document.getElementById("priority_summary").value;
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

            if (rejectionSection != null) {
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
                    rejectionSection.classList.add("govuk-form-group--error");
                }
            }
        });
    },
    // SHOULD DELETE THE FOLLOWING JS METHODS WHEN PB100 IS REMOVED FROM STATUS PAGE
    optionalRejectionSummary: function (
        top_barrier_status_id,
        rejection_summary_id
    ) {
        const topBarrierStatusInputContainer = jessie.queryOne(
            `#${top_barrier_status_id}`
        );
        const rejectionSummaryInputContainer = jessie.queryOne(
            `#${rejection_summary_id}`
        );

        // if rejection container doesn't exist, return
        if (
            !topBarrierStatusInputContainer ||
            !rejectionSummaryInputContainer
        ) {
            return;
        }
        rejectionSummaryInputContainer.style = "display: none";

        // get radio input that has No as label
        const yesRadioInput = jessie.queryOne(`#${top_barrier_status_id}-1`);
        const noRadioInput = jessie.queryOne(`#${top_barrier_status_id}-2`);

        const handleRejectionVisibility = function () {
            if (noRadioInput.checked) {
                rejectionSummaryInputContainer.style = "display: block";
            } else {
                rejectionSummaryInputContainer.style = "display: none";
            }
        };

        // add event listener to top barrier status
        yesRadioInput.addEventListener("change", function () {
            handleRejectionVisibility();
        });
        noRadioInput.addEventListener("change", function () {
            handleRejectionVisibility();
        });
    },
    toggleNoticeOnPriorityRadioChange: function (
        top_barrier_status_id,
        notice_id
    ) {
        const topBarrierStatusInputContainer = jessie.queryOne(
            `#${top_barrier_status_id}`
        );
        const noticeContainer = jessie.queryOne(`#${notice_id}`);
        if (!topBarrierStatusInputContainer || !noticeContainer) {
            // if notice container doesn't exist, return
            return;
        }
        noticeContainer.style = "display: none";

        const yesRadioInput = jessie.queryOne(`#${top_barrier_status_id}-1`);
        const noRadioInput = jessie.queryOne(`#${top_barrier_status_id}-2`);

        const handleRejectionVisibility = function () {
            noticeContainer.style = "display: block";
        };

        // add event listener to top barrier status
        yesRadioInput.addEventListener("change", function () {
            handleRejectionVisibility();
        });
        noRadioInput.addEventListener("change", function () {
            handleRejectionVisibility();
        });
    },
};
