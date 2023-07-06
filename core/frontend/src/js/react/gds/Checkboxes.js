import { Checkboxes } from "govuk-frontend";

function GDSCheckboxes() {
    Array.from(
        document.querySelectorAll('[data-module="govuk-checkboxes"]')
    ).forEach((checkboxes) => {
        new Checkboxes(checkboxes).init();
    });
}

export default GDSCheckboxes;
