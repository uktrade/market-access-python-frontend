import { Radios } from "govuk-frontend";

function GDSRadios() {
    Array.from(
        document.querySelectorAll('[data-module="govuk-radios"]')
    ).forEach((radios) => {
        new Radios(radios).init();
    });
}

export default GDSRadios;
