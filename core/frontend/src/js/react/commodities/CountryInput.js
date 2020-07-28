import React from "react";


function CountryInput(props) {
  return (
    <div className="govuk-form-group govuk-!-margin-top-5">
      <fieldset className="govuk-fieldset">
        <legend className="govuk-fieldset__legend">
          Which location are the commodity codes from?
        </legend>

        <div className="govuk-radios country govuk-radios--inline" data-module="radios">
          {props.countries.map((country, index) =>
            <div className="govuk-radios__item">
              <input
                className="govuk-radios__input"
                id={"country-" + country.id}
                name="country"
                type="radio"
                value={country.id}
                defaultChecked={country.id == props.countryId}
                onChange={props.onChange}
              />
              <label className="govuk-label govuk-radios__label" for={"country-" + country.id}>{country.name}</label>
            </div>
          )}
        </div>
      </fieldset>
    </div>
  )
}


export default CountryInput
