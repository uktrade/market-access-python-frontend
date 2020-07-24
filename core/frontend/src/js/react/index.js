import React from "react";
import ReactDOM from 'react-dom'

import CommodityForm from "./commodities/CommodityForm"
import {getCSRFToken} from "./utils"


function renderCommodities(confirmedCommodities, countries) {
  const csrfToken = getCSRFToken()
  ReactDOM.render(
    <CommodityForm
      csrfToken={csrfToken}
      confirmedCommodities={confirmedCommodities}
      countries={countries}
    />,
    document.getElementById('react-app')
  );
}


export {renderCommodities}
