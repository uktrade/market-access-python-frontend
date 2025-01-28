import React from "react";
import ReactDOM from "react-dom";

import CommodityForm from "./commodities/CommodityForm";
import CompaniesForm from "./companies/CompaniesForm";
import LocationFilter from "./search/LocationFilter";
import { getCSRFToken, getCheckboxValues } from "./utils";
import MultiSelectFilter from "./search/MultiSelectFilter";
import TextAreaWithMentions from "./forms/TextAreaWithMentions";
import RisksAndMitigationForm from "./forms/RisksAndMitigationForm";
import EmailSearchAutocomplete from "./forms/EmailSearchAutocomplete";
import { renderAsyncSearchResults } from "./search/AsyncSearchResultsBox";
import GDSTabs from "./gds/Tabs";
import GDSRadios from "./gds/Radios";
import GDSCheckboxes from "./gds/Checkboxes";
import { renderBarChart } from "./dashboard/charts";
import { renderApplyFilterButton } from "./dashboard/button";

function renderCommodityForm(
    confirmedCommodities,
    locations,
    label,
    helpText,
    isReportJourney = false,
    nextUrl = null,
) {
    const csrfToken = getCSRFToken();
    ReactDOM.render(
        <CommodityForm
            csrfToken={csrfToken}
            confirmedCommodities={confirmedCommodities}
            locations={locations}
            label={label}
            helpText={helpText}
            isReportJourney={isReportJourney}
            nextUrl={nextUrl}
        />,
        document.getElementById("react-app"),
    );
}

function renderCompaniesForm(searchLabel, searchHelpText) {
    ReactDOM.render(
        <CompaniesForm
            searchLabel={searchLabel}
            searchHelpText={searchHelpText}
        />,
        document.getElementById("react-app"),
    );
}

function renderLocationFilter(
    countryElement,
    tradingBlocElement,
    tradingBlocData,
    adminAreaData,
    adminAreasCountries,
) {
    const label = countryElement.querySelector("legend").textContent.trim();
    const countries = getCheckboxValues(countryElement);
    const tradingBlocs = getCheckboxValues(tradingBlocElement);

    if (tradingBlocElement) {
        tradingBlocElement.remove();
    }
    ReactDOM.render(
        <LocationFilter
            label={label}
            countries={countries}
            tradingBlocs={tradingBlocs}
            tradingBlocData={tradingBlocData}
            adminAreaData={adminAreaData}
            adminAreasCountries={adminAreasCountries}
        />,
        countryElement,
    );
}

function renderMultiSelectFilter(
    htmlElementId,
    placeholder = null,
    labelClasses = null,
    containerClasses = null,
    secondaryOptions = null,
) {
    let placeholderString = placeholder
        ? placeholder
        : `Search ${htmlElementId}s`;
    let htmlElement = document.getElementById(htmlElementId);
    const label = htmlElement.querySelector("legend").textContent.trim();
    const options = getCheckboxValues(htmlElement);

    ReactDOM.render(
        <MultiSelectFilter
            label={label}
            options={options}
            inputId={htmlElementId}
            placeholder={placeholderString}
            labelClasses={labelClasses}
            containerClasses={containerClasses}
            secondaryOptions={secondaryOptions}
        />,
        htmlElement,
    );
}

function renderTextAreaWithMentions(
    htmlElementId = "note-textarea-container",
    placeholder = null,
    labelClasses = null,
    containerClasses = null,
    trigger = undefined,
) {
    const addNoteElement = document.getElementById(htmlElementId);
    const nativeTextarea = addNoteElement.querySelector("textarea");

    const name = nativeTextarea.getAttribute("name");
    const id = nativeTextarea.getAttribute("id");
    const preExistingText = nativeTextarea.value;

    ReactDOM.render(
        <TextAreaWithMentions
            textAreaId={id}
            textAreaName={name}
            preExistingText={preExistingText}
            trigger={trigger}
        />,
        addNoteElement,
    );
}

function renderInputSelectWithMentions(
    htmlElementId = "note-textarea-container",
    placeholder = null,
    labelClasses = null,
    containerClasses = null,
    trigger = undefined,
    autofocus = true,
) {
    console.log("setting up input with mentions", htmlElementId, trigger);

    const inputContainerElement = document.getElementById(htmlElementId);
    const nativeTextarea = inputContainerElement.querySelector("input");

    const name = nativeTextarea.getAttribute("name");
    const id = nativeTextarea.getAttribute("id");
    const preExistingText = nativeTextarea.value;

    ReactDOM.render(
        <TextAreaWithMentions
            idPrefix={""}
            isSingleLine={true}
            textAreaId={id}
            textAreaName={name}
            preExistingText={preExistingText}
            trigger={trigger}
            autofocus={autofocus}
        />,
        inputContainerElement,
    );
}

/**
 * @param {string} fieldID
 */
function renderEmailSearchAutocomplete(fieldID) {
    const field = document.getElementById(fieldID),
        // @ts-ignore
        fieldlLabel = field.labels[0],
        wrapperElement = field.closest(".dmas_autocomplete_wrapper");
    ReactDOM.render(
        <EmailSearchAutocomplete field={field} label={fieldlLabel} />,
        wrapperElement,
    );
}

function renderRisksAndMitigationForm() {
    const container = document.createElement("div");
    ReactDOM.render(<RisksAndMitigationForm />, container);
}

export {
    renderCommodityForm,
    renderCompaniesForm,
    renderLocationFilter,
    renderMultiSelectFilter,
    renderTextAreaWithMentions,
    renderInputSelectWithMentions,
    renderEmailSearchAutocomplete,
    renderRisksAndMitigationForm,
    renderAsyncSearchResults,
    GDSTabs,
    GDSRadios,
    GDSCheckboxes,
    renderApplyFilterButton,
    renderBarChart,
};
