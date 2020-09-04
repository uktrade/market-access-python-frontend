import React from "react";


function LocationInput(props) {
  return (
    <div className="govuk-form-group govuk-!-margin-top-5">
      <fieldset className="govuk-fieldset">
        <legend className="govuk-fieldset__legend">
          Which location are the commodity codes from?
        </legend>

        <div className="govuk-radios location govuk-radios--inline" data-module="radios">
          {props.locations.map((location, index) =>
            <div className="govuk-radios__item">
              <input
                className="govuk-radios__input"
                id={"location-" + location.id}
                name="location"
                type="radio"
                value={location.id}
                defaultChecked={location.id == props.locationId}
                onChange={props.onChange}
              />
              <label className="govuk-label govuk-radios__label" for={"location-" + location.id}>{location.name}</label>
            </div>
          )}
        </div>
      </fieldset>
    </div>
  )
}


export default LocationInput
