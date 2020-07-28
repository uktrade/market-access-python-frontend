import React from "react";
import ReactDOM from 'react-dom'

import CommodityForm from "./commodities/CommodityForm"
import {getCSRFToken} from "./utils"


function renderCommodityForm(confirmedCommodities, countries, label, helpText) {
  const csrfToken = getCSRFToken()
  ReactDOM.render(
    <CommodityForm
      csrfToken={csrfToken}
      confirmedCommodities={confirmedCommodities}
      countries={countries}
      label={label}
      helpText={helpText}
    />,
    document.getElementById('react-app')
  );
}


export {renderCommodities}
