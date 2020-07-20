import React from "react";
import ReactDOM from 'react-dom'

import CommodityForm from "./commodities/CommodityForm"


function renderCommodities(csrfToken) {
    ReactDOM.render(<CommodityForm csrfToken={csrfToken} />, document.getElementById('react-app'));
}

export {renderCommodities}
