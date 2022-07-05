import { FieldChoice } from "../types";

export const denormalizeFieldChoices = (
    choices: [string, string][]
): FieldChoice[] => {
    return choices.map(([value, label]) => ({
        label,
        value,
    }));
};
