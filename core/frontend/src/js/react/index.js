import React from "react";
import ReactDOM from "react-dom";

import CommodityForm from "./commodities/CommodityForm";
import LocationFilter from "./search/LocationFilter";
import { getCSRFToken, getCheckboxValues } from "./utils";
import MultiSelectFilter from "./search/MultiSelectFilter";
import TextAreaWithMentions from "./forms/TextAreaWithMentions";

function renderCommodityForm(
    confirmedCommodities,
    locations,
    label,
    helpText,
    isReportJourney = false,
    nextUrl = null
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
        document.getElementById("react-app")
    );
}

function renderLocationFilter(
    countryElement,
    tradingBlocElement,
    tradingBlocData
) {
    const label = countryElement.querySelector("legend").textContent.trim();
    const countries = getCheckboxValues(countryElement);
    const tradingBlocs = getCheckboxValues(tradingBlocElement);

    tradingBlocElement.remove();
    ReactDOM.render(
        <LocationFilter
            label={label}
            countries={countries}
            tradingBlocs={tradingBlocs}
            tradingBlocData={tradingBlocData}
        />,
        countryElement
    );
}

function renderMultiSelectFilter(
    htmlElementId,
    placeholder = null,
    labelClasses = null,
    containerClasses = null,
    secondaryOption = null
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
            secondaryOptionFieldName={secondaryOption?.fieldName}
            secondaryOptionLabel={secondaryOption?.label}
        />,
        htmlElement
    );
}

function renderTextAreaWithMentions(
    htmlElementId = "note-textarea-container",
    placeholder = null,
    labelClasses = null,
    containerClasses = null,
    trigger = undefined
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
        addNoteElement
    );
}

function renderInputSelectWithMentions(
    htmlElementId = "note-textarea-container",
    placeholder = null,
    labelClasses = null,
    containerClasses = null,
    trigger = undefined,
    autofocus = true
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
        inputContainerElement
    );
}

export {
    renderCommodityForm,
    renderLocationFilter,
    renderMultiSelectFilter,
    renderTextAreaWithMentions,
    renderInputSelectWithMentions,
};
