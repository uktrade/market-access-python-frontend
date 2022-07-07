import React from "react";
import { denormalizeFieldChoices } from "../../forms/utils";
import { FieldChoice, FieldDescription } from "../../types";

// interface SelectField {
//     help_text: string;
//     label: string;
//     name: string;
//     field: {
//         choices: { [id: string]: string };
//     };
// }

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

            {/* form errors here */}

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
                        // console.log("optGroup", optGroup);
                        return (
                            <optgroup key={optGroup} label={optGroup}>
                                {optGroups[optGroup].map(({ label, value }) => {
                                    // console.log("label", label, "value", value);
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

// {% for value, label in field.field.choices %}
//             {% if label.0|add:"x" == "" %}
//                 {% with group_name=value group_choices=label %}
//                     <optgroup label="{ group_name }">
//                         {% for value, label in group_choices %}
//                             <option{% if option_classes %} className="{ option_classes }"{% endif %} value="{ value }"{% if value == field.value %} selected{% endif %}>{ label }</option>
//                         {% endfor %}
//                     </optgroup>
//                 {% endwith %}
//             {% else %}
//                 <option value="{ value }"{% if value == field.value %} selected{% endif %}>{ label }</option>
//             {% endif %}
//         {% endfor %}
