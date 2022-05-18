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
        noticeContainer.style = "display: none";
        if (!topBarrierStatusInputContainer || !noticeContainer) {
            // if notice container doesn't exist, return
            return;
        }

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
