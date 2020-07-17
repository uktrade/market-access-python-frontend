import React from "react";
import ReactDOM from 'react-dom'

import CommodityForm from "./commodities/CommodityForm"


function renderCommodities() {
    ReactDOM.render(<CommodityForm />, document.getElementById('react-app'));
}

export {renderCommodities}
