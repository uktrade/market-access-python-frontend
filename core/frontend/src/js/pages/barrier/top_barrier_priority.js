ma.pages.topBarrierPriority = {
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
    toggleTopPriorityForValidBasicPriorites: function () {
        // Get page components
        const topPriorityConsiderationContainer =
            document.getElementById("top_barrier");
        const topPriorityDescriptionContainer = document.getElementById(
            "priority_summary-container"
        );
        const regionalRadioInput = document.getElementById("priority_level-1");
        const countryRadioInput = document.getElementById("priority_level-2");
        const watchlistRadioInput = document.getElementById("priority_level-3");
        const topPriorityConsiderationYesRadio =
            document.getElementById("top_barrier-1");
        const topPriorityConsiderationNoRadio =
            document.getElementById("top_barrier-2");

        // we need topPriorityConsiderationContainer to be visible if these django variables are true: user_is_top_priority_moderator and is_top_priority_requested
        const moderatorInformation = document.getElementById(
            "requested-top-priority-moderator-display"
        );
        if (moderatorInformation != null) {
            console.log("HERE");
        }
        //console.log("Is admin = " + is_top_priority_requested)
        //console.log("Is requested = " + `${is_top_priority_requested}`)

        // Set initial visibility of collapsable sections
        if (topPriorityConsiderationContainer != null) {
            // Show the panel if either valid priority level checked, or the barrier is existing Top Priority
            if (
                regionalRadioInput.checked == true ||
                countryRadioInput.checked == true ||
                moderatorInformation != null
            ) {
                topPriorityConsiderationContainer.style = "display: block";
            } else {
                topPriorityConsiderationContainer.style = "display: none";
            }
        }
        if (topPriorityDescriptionContainer != null) {
            if (
                topPriorityDescriptionContainer != null &&
                topPriorityConsiderationYesRadio.checked == true
            ) {
                topPriorityDescriptionContainer.style = "display: block";
            } else {
                topPriorityDescriptionContainer.style = "display: none";
            }
        }

        const showTopPriorityConsideration = function () {
            topPriorityConsiderationContainer.style = "display: block";
        };
        const hideTopPriorityConsideration = function () {
            // Hide the questions and notice for Top 100
            topPriorityConsiderationContainer.style = "display: none";
            const topPriorityNotice = document.getElementById(
                "top-priority-request-notice"
            );
            topPriorityDescriptionContainer.style = "display: none";
            topPriorityNotice.style = "display: none";
            // Set the consideration question to 'No' to avoid accidental submission of a 'Yes'
            topPriorityConsiderationYesRadio.checked = false;
            topPriorityConsiderationNoRadio.checked = true;
        };

        // Add change listeners to the radio buttons
        regionalRadioInput.addEventListener("change", function () {
            if (topPriorityConsiderationContainer != null) {
                showTopPriorityConsideration();
            }
        });
        countryRadioInput.addEventListener("change", function () {
            if (topPriorityConsiderationContainer != null) {
                showTopPriorityConsideration();
            }
        });
        watchlistRadioInput.addEventListener("change", function () {
            if (
                topPriorityConsiderationContainer != null &&
                moderatorInformation == null
            ) {
                // Hide the top_barrier container as long as the viewer is not an admin being asked for approval
                hideTopPriorityConsideration();
            }
        });
    },
    toggleDescriptionOnPriorityRadioChange: function (
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

        const topPriorityDescriptionContainer = document.getElementById(
            "priority_summary-container"
        );
        topPriorityDescriptionContainer.style = "display: none";

        const showTopPriorityDescription = function () {
            noticeContainer.style = "display: block";
            topPriorityDescriptionContainer.style = "display: block";
        };

        const hideTopPriorityDescription = function () {
            noticeContainer.style = "display: none";
            topPriorityDescriptionContainer.style = "display: none";
        };

        // add event listener to top barrier status
        yesRadioInput.addEventListener("change", function () {
            showTopPriorityDescription();
        });
        noRadioInput.addEventListener("change", function () {
            hideTopPriorityDescription();
        });
    },
};
