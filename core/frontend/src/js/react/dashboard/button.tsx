import React from "react";
import ReactDOM from "react-dom";

interface ApplyFilterButtonProps {
    text: string;
}

interface updateBarrierInsight {
    (submitUrl: string): void;
}

interface HandleClickEvent extends React.MouseEvent<HTMLButtonElement> {
    preventDefault: () => void;
}

/**
 * ApplyFilterButton component.
 *
 * This component renders a button that, when clicked, applies filters to update the dashboard.
 *
 * @param {ApplyFilterButtonProps} props - The properties for the ApplyFilterButton component.
 *
 * @returns {JSX.Element} The rendered button component.
 *
 * @component
 *
 * @example
 * <ApplyFilterButton text="Apply Filters" />
 *
 * @function
 *
 * @name ApplyFilterButton
 *
 * @description
 * The ApplyFilterButton component is responsible for handling the click event to apply filters
 * and update the dashboard. It fetches the updated content from the server and replaces the
 * relevant sections of the page with the new content.
 *
 * @param {React.MouseEvent<HTMLButtonElement>} event - The click event.
 *
 * @async
 * @function
 * @name handleClick
 *
 * @description
 * The handleClick function is triggered when the button is clicked. It prevents the default
 * form submission, constructs a new query string from the form data, updates the URL, and
 * fetches the updated content to replace the relevant sections of the page.
 *
 * @param {string} submitUrl - The URL to fetch the updated content from.
 *
 * @async
 * @function
 * @name updateBarrierInsight
 *
 * @description
 * The updateBarrierInsight function fetches the updated content from the server and replaces
 * the relevant sections of the page with the new content.
 */
const ApplyFilterButton: React.FC<ApplyFilterButtonProps> = (props: ApplyFilterButtonProps): JSX.Element => {

    const filterForm = document.querySelector<HTMLFormElement>("#filters-form");

    const updateBarrierInsight: updateBarrierInsight = async (submitUrl: string): Promise<void> => {
        const response = await fetch(submitUrl);
        const responseText = await response.text();
        const tempElement = document.createElement("html");
        tempElement.innerHTML = responseText;
        const barrierInsight = tempElement.querySelector("#barrier-insights");
        const barrierChart = tempElement.querySelector("#barrier-charts");

        if (barrierInsight) {
            const barrierInsightContainer = document.querySelector("#barrier-insights");
            barrierInsightContainer.innerHTML = barrierInsight.innerHTML;
        }
        if (barrierChart) {
            const barrierChartContainer = document.querySelector("#barrier-charts");
            barrierChartContainer.innerHTML = barrierChart.innerHTML;
        }
    };

    const handleClick = async (event: HandleClickEvent) => {
        // prevent the default action
        event.preventDefault();

        const currentURLQuerystring = document.location.search;

        // transform form data to FormData object
        const formData = new FormData(filterForm as HTMLFormElement);

        // only pass in formdata that has a value
        for (const [key, value] of formData.entries()) {
            if (value === "" || value === null) {
                formData.delete(key);
            }
        }

        const queryString = new URLSearchParams(formData as any).toString();

        if (queryString === currentURLQuerystring) return;

        const formAction = filterForm.action.split("?")[0];
        const submitURL = `${formAction}?${queryString}`;
        window.history.pushState({}, document.title, submitURL);

        // update the dashboard
        updateBarrierInsight(submitURL);

    };

    return (
        <button
            className={`govuk-button govuk-button--full-width`}
            type="button"
            onClick={handleClick}
            data-module="govuk-button"
        >
            {props.text}
        </button>
    );
};

export const renderApplyFilterButton = (elementId: string, buttonText: any) => {
    const element = document.getElementById(elementId);
    const text = buttonText || "Apply filters";
    ReactDOM.render(
        <ApplyFilterButton
            text={text}
        />,
        element,
    );
};
