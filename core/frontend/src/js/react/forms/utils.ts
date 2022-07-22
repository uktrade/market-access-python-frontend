import { FieldChoice } from "../types";

export const denormalizeFieldChoices = (
    choices: [string, string][]
): FieldChoice[] => {
    // maps a Django choice tuple list to a FieldChoice list
    return choices.map(([value, label]) => ({
        label,
        value,
    }));
};
