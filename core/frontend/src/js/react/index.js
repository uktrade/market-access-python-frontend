import React from "react";
import ReactDOM from 'react-dom'

import CommodityForm from "./commodities/CommodityForm"
import LocationFilter from "./search/LocationFilter"
import {getCSRFToken, getCheckboxValues} from "./utils"


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


export {renderCommodityForm, renderLocationFilter}
