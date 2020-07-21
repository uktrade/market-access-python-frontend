import React from "react";
import ReactDOM from 'react-dom'

import CommodityForm from "./commodities/CommodityForm"


function renderCommodities(csrfToken, confirmedCommodities) {
    ReactDOM.render(<CommodityForm csrfToken={csrfToken} confirmedCommodities={confirmedCommodities} />, document.getElementById('react-app'));
}

export {renderCommodities}
