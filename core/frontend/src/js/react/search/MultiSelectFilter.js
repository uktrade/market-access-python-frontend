import TypeAhead from "../forms/TypeAhead";
import React, { useState } from "react";

function MultiSelectFilter(props) {
    let labelClasses = props.labelClasses
        ? props.labelClasses
        : "filter-items__label";
    labelClasses = `govuk-label ${labelClasses}`;
    const initialSelectedOptions = props.options.reduce((selected, option) => {
        if (option.checked) selected.push(option);
        return selected;
    }, []);
    const initialSelectedOptionIds = initialSelectedOptions.map(
        (option) => option.value
    );
    const [selectedOptionIds, setSelectedOptionIds] = useState(
        initialSelectedOptionIds
    );

    // A multi-select field can have a checkbox below it called secondary option
    // if props are provided generated below with appropriate details
    const { secondaryOptionLabel, secondaryOptionFieldName } = props;
    const urlSearchParams = new URLSearchParams(window.location.search);
    const queryParams = Object.fromEntries(urlSearchParams.entries());
    const defaultSecondaryOptionValue = secondaryOptionFieldName
        ? queryParams[secondaryOptionFieldName]
        : false;
    const [secondaryOptionValue, setSecondaryOptionValue] = useState(
        defaultSecondaryOptionValue
    );

    const handleOptionSelect = (value, meta) => {
        if (meta.action === "select-option") {
            let option = meta.option.value;
            setSelectedOptionIds(selectedOptionIds.concat(option));
        } else {
            let option = meta.removedValue.value;
            setSelectedOptionIds(
                selectedOptionIds.filter((item) => item !== option)
            );
        }
    };

    return (
        <div className="govuk-form-group">
            <fieldset className="govuk-fieldset">
                <legend className="govuk-fieldset__legend filter-items__label filter-group__label visually-hidden">
                    {props.label}
                </legend>

                <label className={labelClasses} htmlFor={props.inputId}>
                    {props.label}
                </label>

                <TypeAhead
                    inputId={props.inputId}
                    options={props.options}
                    name={props.inputId}
                    onChange={handleOptionSelect}
                    placeholder={props.placeholder}
                    defaultValue={initialSelectedOptions}
                    containerClasses={props.containerClasses}
                />

                {secondaryOptionFieldName && secondaryOptionLabel ? (
                    <div className="checkbox-filter govuk-!-width-full">
                        <div className="checkbox-filter__item">
                            <input
                                className="checkbox-filter__input"
                                id={`secondary-option-${secondaryOptionFieldName}`}
                                name={secondaryOptionFieldName}
                                type="checkbox"
                                checked={secondaryOptionValue}
                                onChange={(event) =>
                                    setSecondaryOptionValue(
                                        !secondaryOptionValue
                                    )
                                }
                            />
                            <label
                                className="govuk-label checkbox-filter__label"
                                htmlFor={`secondary-option-${secondaryOptionFieldName}`}
                            >
                                {secondaryOptionLabel}
                            </label>
                        </div>
                    </div>
                ) : null}
            </fieldset>
        </div>
    );
}

export default MultiSelectFilter;
