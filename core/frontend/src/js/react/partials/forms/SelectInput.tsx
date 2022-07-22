import React from "react";
import { denormalizeFieldChoices } from "../../forms/utils";
import { FieldChoice, FieldDescription } from "../../types";

interface SelectInputProps {
    field: FieldDescription;
    value: string;
    overriddenChoices?: FieldChoice[];
    onChange: (value: string) => void;
    placeholder: string;
}

export const SelectInput: React.FC<SelectInputProps> = ({
    field,
    value,
    overriddenChoices,
    placeholder,
    onChange,
}) => {
    const choices = overriddenChoices || denormalizeFieldChoices(field.choices);

    const optGroups = choices.reduce((acc, choice) => {
        const optGroup = choice.optGroup;
        if (!acc[optGroup]) {
            acc[optGroup] = [];
        }
        if (!optGroup) {
            return acc;
        }
        acc[optGroup].push(choice);
        return acc;
    }, {});

    const nonOptChoices = choices.filter((choice) => !choice.optGroup);

    const handleInputChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
        onChange(event.target.value);
    };

    return (
        <div
            id="{ field.name }"
            className="{% form_group_classes field.errors %}"
        >
            <label className="govuk-label govuk-label--s">{field.label}</label>

            {field.help_text && (
                <span className="govuk-hint govuk-hint--s">
                    {field.help_text}
                </span>
            )}

            <select
                className="govuk-select"
                id={field.name}
                name={field.name}
                onChange={handleInputChange}
                value={value}
            >
                <option value={""} key="no-value">
                    {placeholder}
                </option>
                {nonOptChoices.map(({ label, value }) => {
                    return (
                        <option value={value} key={value}>
                            {label}
                        </option>
                    );
                })}
                {optGroups &&
                    Object.keys(optGroups).map((optGroup) => {
                        return (
                            <optgroup key={optGroup} label={optGroup}>
                                {optGroups[optGroup].map(({ label, value }) => {
                                    return (
                                        <option value={value} key={value}>
                                            {label}
                                        </option>
                                    );
                                })}
                            </optgroup>
                        );
                    })}
            </select>
        </div>
    );
};
