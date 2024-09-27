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
        (option) => option.value,
    );
    const [selectedOptionIds, setSelectedOptionIds] = useState(
        initialSelectedOptionIds,
    );

    // A multi-select field can have a checkbox below it called secondary option
    // if props are provided generated below with appropriate details

    const { secondaryOptions } = props;
    const urlSearchParams = new URLSearchParams(window.location.search);
    const queryParams = Object.fromEntries(urlSearchParams.entries());
    const defaultSecondaryOptionValues = secondaryOptions
        ? secondaryOptions.reduce((accum, option) => {
              accum[option.fieldName] = queryParams[option.fieldName] || false;
              return accum;
          }, {})
        : {};

    const [secondaryOptionValues, setSecondaryOptionValues] = useState(
        defaultSecondaryOptionValues,
    );

    // To update a specific checkbox state, you can use a function like:
    const handleSecondaryOptionChange = (fieldName) => {
        setSecondaryOptionValues((prevValues) => ({
            ...prevValues,
            [fieldName]: !prevValues[fieldName],
        }));
    };

    const handleOptionSelect = (value, meta) => {
        if (meta.action === "select-option") {
            let option = meta.option.value;
            setSelectedOptionIds((prevState) => {
                const newOption = [...prevState, option];
                if (props.onChange) {
                    props.onChange({ name: props.inputId, value: newOption });
                }
                return newOption;
            });
        } else {
            let option = meta.removedValue.value;
            setSelectedOptionIds((prevState) => {
                const newOptions = prevState.filter((item) => item !== option)
                if (props.onChange) {
                    props.onChange({ name: props.inputId, value: newOptions });
                }
                return newOptions;
                }
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

                {secondaryOptions && secondaryOptions.length > 0 ? (
                    <div className="checkbox-filter govuk-!-width-full">
                        {props.secondaryOptions.map((option, index) => (
                            <div className="checkbox-filter__item" key={index}>
                                <input
                                    className="checkbox-filter__input"
                                    id={`secondary-option-${option.fieldName}`}
                                    name={option.fieldName}
                                    type="checkbox"
                                    checked={
                                        secondaryOptionValues[option.fieldName]
                                    }
                                    onChange={() =>
                                        handleSecondaryOptionChange(
                                            option.fieldName,
                                        )
                                    }
                                />
                                <label
                                    className="govuk-label checkbox-filter__label"
                                    htmlFor={`secondary-option-${option.fieldName}`}
                                >
                                    {option.label}
                                </label>
                            </div>
                        ))}
                    </div>
                ) : null}
            </fieldset>
        </div>
    );
}

export default MultiSelectFilter;
