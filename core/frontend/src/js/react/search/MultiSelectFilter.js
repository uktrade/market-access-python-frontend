import TypeAhead from "../forms/TypeAhead";
import React, {useState} from "react";


function MultiSelectFilter(props) {
    const initialSelectedOptions = props.options.reduce((selected, option) => {
        if (option.checked) selected.push(option)
        return selected
    }, []);
    const initialSelectedOptionIds = initialSelectedOptions.map(option => option.value)
    const [selectedOptionIds, setSelectedOptionIds] = useState(initialSelectedOptionIds)

    const handleOptionSelect = (value, meta) => {
        if (meta.action === "select-option") {
            let option = meta.option.value
            setSelectedOptionIds(selectedOptionIds.concat(option))
        } else {
            let option = meta.removedValue.value
            setSelectedOptionIds(
                selectedOptionIds.filter(item => item !== option)
            )
        }
    }

    return (
        <div className="govuk-form-group">
            <fieldset className="govuk-fieldset">
                <legend className="govuk-fieldset__legend filter-items__label filter-group__label visually-hidden">
                    {props.label}
                </legend>

                <label className="govuk-label filter-items__label" htmlFor={props.inputId}>
                    {props.label}
                </label>

                <TypeAhead
                    inputId={props.inputId}
                    options={props.options}
                    name={props.inputId}
                    onChange={handleOptionSelect}
                    placeholder={props.placeholder}
                    defaultValue={initialSelectedOptions}
                />

            </fieldset>

        </div>
    )
}

export default MultiSelectFilter
