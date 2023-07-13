ma.pages.report.aboutWizardStep = function () {
    // About page needs to hide save and exit button on parent wizard template
    const saveExitButton = document.getElementById("save-exit-button");
    saveExitButton.style.display = "none";

    // Back button on wizard template should navigate to report-barrier landing page
    const wizardBackButton = document.getElementById("form-wizard-back-button");
    wizardBackButton.style.display = "none";
};
