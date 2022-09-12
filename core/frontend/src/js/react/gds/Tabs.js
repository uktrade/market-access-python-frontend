// require.context("govuk-frontend/govuk/assets");
import { Tabs } from "govuk-frontend";

function GDSTabs() {
    Array.from(document.querySelectorAll('[data-module="govuk-tabs"]')).forEach(
        (tabs) => {
            new Tabs(tabs).init();
        }
    );
}

export default GDSTabs;
