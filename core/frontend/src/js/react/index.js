import React from "react";
import ReactDOM from 'react-dom'

import CommodityForm from "./commodities/CommodityForm"
import LocationFilter from "./search/LocationFilter"
import { getCSRFToken, getCheckboxValues } from "./utils"
import MultiSelectFilter from "./search/MultiSelectFilter";
import TextAreaWithMentions from './forms/TextAreaWithMentions';

function renderCommodityForm(confirmedCommodities, locations, label, helpText) {
  const csrfToken = getCSRFToken()
  ReactDOM.render(
    <CommodityForm
      csrfToken={csrfToken}
      confirmedCommodities={confirmedCommodities}
      locations={locations}
      label={label}
      helpText={helpText}
    />,
    document.getElementById('react-app')
  );
}


function renderLocationFilter(countryElement, tradingBlocElement, tradingBlocData) {
  const label = countryElement.querySelector('legend').textContent.trim()
  const countries = getCheckboxValues(countryElement)
  const tradingBlocs = getCheckboxValues(tradingBlocElement)

  tradingBlocElement.remove()
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


function renderMultiSelectFilter(htmlElementId, placeholder = null, labelClasses = null, containerClasses = null) {
  let placeholderString = placeholder ? placeholder : `Search ${htmlElementId}s`
  let htmlElement = document.getElementById(htmlElementId)
  const label = htmlElement.querySelector('legend').textContent.trim()
  const options = getCheckboxValues(htmlElement)

  ReactDOM.render(
    <MultiSelectFilter
      label={label}
      options={options}
      inputId={htmlElementId}
      placeholder={placeholderString}
      labelClasses={labelClasses}
      containerClasses={containerClasses}
    />,
    htmlElement
  );
}

function renderTextAreaWithMentions(htmlElementId, placeholder = null, labelClasses = null, containerClasses = null) {

  const addNoteElement = document.getElementById("note-textarea-container")
  const nativeTextarea = addNoteElement.querySelector("textarea")

  const name = nativeTextarea.getAttribute("name")
  const id = nativeTextarea.getAttribute("id")

  ReactDOM.render(
    <TextAreaWithMentions textAreaId={id} textAreaName={name} />,
    addNoteElement
  )
}


export { renderCommodityForm, renderLocationFilter, renderMultiSelectFilter, renderTextAreaWithMentions }
