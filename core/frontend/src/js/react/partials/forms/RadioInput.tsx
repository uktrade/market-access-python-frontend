import React from "react";
import slugify from "slugify";
import { denormalizeFieldChoices } from "../../forms/utils";
import { FieldChoice, FieldDescription, FieldOverrides } from "../../types";
import { FieldErrorList } from "./FieldError";

interface RadioInputOptionProps {
    value: string;
    label: string;
    name: string;
    selectedValue: string;
    onChange: (value: string, checked: boolean) => void;
}

const RadioInputOption: React.FC<RadioInputOptionProps> = ({
    value,
    label,
    name,
    selectedValue,
    onChange,
}) => {
    const isChecked = value === selectedValue;
    const id = `${label}-${selectedValue}`;

    console.log("RadioInputOption", {
        value,
        label,
        name,
        selectedValue,
        isChecked,
        id,
    });

    const handleRadioChange = (event) => {
        onChange(value, true);
    };

    return (
        <div className="govuk-radios__item" onClick={handleRadioChange}>
            <input
                className="govuk-radios__input"
                id={id}
                name={name}
                type="radio"
                value={value}
                checked={isChecked}
                onChange={handleRadioChange}
            />
            <label className="govuk-label govuk-radios__label">{label}</label>
        </div>
    );
};

interface RadioInputProps {
    field: FieldDescription;
    onChange: (value: string) => void;
    fieldOverrides?: FieldOverrides;
    value: string;
    fieldErrors?: string[];
}

export const RadioInput: React.FC<RadioInputProps> = ({
    field,
    value,
    onChange,
    fieldOverrides,
    fieldErrors,
}) => {
    const choices =
        fieldOverrides?.choices || denormalizeFieldChoices(field.choices);

    const label = fieldOverrides?.label || field.label;
    const help_text = fieldOverrides?.help_text || field.help_text;

    const hasErrors = fieldErrors?.length > 0;

    return (
        <div className="">
            <fieldset className="govuk-fieldset">
                <legend className="govuk-label govuk-label--s">{label}</legend>

                {help_text && (
                    <span className="govuk-hint govuk-hint--s">
                        {help_text}
                    </span>
                )}

                {hasErrors && <FieldErrorList errors={fieldErrors} />}

                <div className="govuk-radios" data-module="radios">
                    {choices.map(({ value: choiceValue, label }) => {
                        return (
                            <RadioInputOption
                                key={choiceValue}
                                value={choiceValue}
                                name={field.name}
                                label={label}
                                selectedValue={value}
                                onChange={onChange}
                            />
                        );
                    })}
                </div>
            </fieldset>
        </div>
    );
};
