import React, { useState } from "react"

import TypeAhead from "../forms/TypeAhead"


function TradingBlocFilter(props) {
  const selectedTradingBlocs = props.tradingBlocs.reduce((selected, tradingBloc) => {
    if (props.selectedTradingBlocIds.includes(tradingBloc.id)) selected.push(tradingBloc)
    return selected;
  }, []);

  return (
      <div className="checkbox-filter govuk-!-width-full">
        {selectedTradingBlocs.map((tradingBloc, index) =>
          <div className="checkbox-filter__item">
            <input
              className="checkbox-filter__input"
              id={"country_trading_bloc-" + index}
              name="country_trading_bloc"
              type="checkbox"
              value={tradingBloc.id}
              defaultChecked={tradingBloc.checked}
            />
            <label className="govuk-label checkbox-filter__label" for={"country_trading_bloc-" + index}>
              {tradingBloc.name}
            </label>
          </div>
        )}
      </div>

  )
}


function LocationFilter(props) {
  const tradingBlocIds = props.tradingBlocs.reduce((ids, tradingBloc) => {
    ids.push(tradingBloc.id)
    return ids;
  }, []);
  const initialSelectedLocations = props.countries.reduce((selected, location) => {
    if (location.checked) selected.push(location.id)
    return selected;
  }, []);
  const [selectedLocations, setSelectedLocations] = useState(initialSelectedLocations)

  const handleLocationSelect = (value, meta) => {
    if (meta.action == "select-option") {
      let location = meta.option.value
      setSelectedLocations(selectedLocations.concat(location))
    } else {
      let location = meta.removedValue.value
      setSelectedLocations(
        selectedLocations.filter(item => item !== location)
      )
    }
  }

  const selectedTradingBlocIds = selectedLocations.reduce((selected, location) => {
    if (tradingBlocIds.includes(location)) selected.push(location)
    return selected;
  }, []);

  const selectedCountryTradingBlocs = props.tradingBlocData.reduce((selected, tradingBloc) => {
    if (selectedLocations.some(item => tradingBloc.country_ids.includes(item))) selected.push(tradingBloc)
    return selected;
  }, []);

  const options = props.countries.reduce((options, country) => {
    options.push({"value": country.id, "label": country.name})
    return options;
  }, []);

  return (
    <div className="govuk-form-group">
      <fieldset className="govuk-fieldset">
        <legend className="govuk-label govuk-label--s">
          {props.label}
        </legend>

        <TypeAhead
          options={options}
          className="multiselect"
          onChange={handleLocationSelect}
          placeholder="Search locations"
        />

        {selectedTradingBlocIds ? (
          <TradingBlocFilter tradingBlocs={props.tradingBlocs} selectedTradingBlocIds={selectedTradingBlocIds} />
        ) : (
          null
        )}

        {selectedCountryTradingBlocs.map((tradingBloc, index) =>
          <div className="checkbox-filter__item">
            <input
              className="checkbox-filter__input"
              id={"country-extra" + index}
              name="country"
              type="checkbox"
              value={tradingBloc.code}
              defaultChecked={tradingBloc.checked}
            />
            <label className="govuk-label checkbox-filter__label" for={"country-extra" + index}>
              {tradingBloc.name}
            </label>
          </div>
        )}

      </fieldset>

    </div>
  )
}


export default LocationFilter
