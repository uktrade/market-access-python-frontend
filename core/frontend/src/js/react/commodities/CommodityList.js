import React from "react";


function CommodityList(props) {
  return (
    <ul className="commodities-list restrict-width">
      {props.commodities.map((commodity, index) => {
        return <li className="commodities-list__item">
            <div className="commodities-list__code">{ commodity.code_display }</div>
            <div className="commodities-list__description">{ commodity.commodity.full_description }</div>

            {props.confirmed ? (
              <button
                name="remove-commodity"
                value={ commodity.code }
                className="commodities-list__remove govuk-button govuk-button--secondary button-as-link"
                data-module="govuk-button"
                onClick={event => {
                  props.onClick(event, index)
                }}>
                Remove
              </button>
            ): (
              <button
                name="confirm-commodity"
                value={ commodity.code }
                className="commodities-list__confirm govuk-button govuk-button--secondary"
                data-module="govuk-button"
                onClick={event => {
                  props.onClick(event, index)
                }}>
                Confirm
              </button>
            )}
        </li>
      })}
    </ul>
  )
}


export default CommodityList;
