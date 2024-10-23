export const getCSRFToken = () => {
    let csrfTokenElements = document.getElementsByName("csrfmiddlewaretoken");
    if (csrfTokenElements.length) {
        // @ts-ignore
        return csrfTokenElements[0].value;
    }
};

export const getCheckboxValues = (/** @type {HTMLElement} */ element) => {
    const filterItems = element.getElementsByClassName("checkbox-filter__item");
    let values = [];

    for (let i = 0; i < filterItems.length; i++) {
        let item = filterItems[i];
        values.push({
            value: item.querySelector("input").value,
            label: item.querySelector("label").textContent.trim(),
            checked: item.querySelector("input").checked,
        });
    }
    return values;
};

/**
 * Normalises a numeric value to a more readable string format using units.
 *
 * @param {number} value - The numeric value to normalize.
 * @returns {string} The normalized value as a string with appropriate units (e.g., "1.5K", "2.3M").
 * @throws {TypeError} If the provided value is not a number.
 */
export const normalizeValue = (/** @type {number} */ value) => {
    if (typeof value !== "number") {
        throw new TypeError("Value must be a number");
    }
    const units = ["K", "M", "B"];
    const thresholds = [1000, 1000000, 1000000000];
    for (let i = thresholds.length - 1; i >= 0; i--) {
        if (value >= thresholds[i]) {
            return (value / thresholds[i]).toFixed(1) + units[i];
        }
    }
    return value.toString();
};
