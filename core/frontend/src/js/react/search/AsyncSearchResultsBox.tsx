import React, { useState } from "react";
import ReactDOM from "react-dom";

const AnchorElementPortal = ({ element }) => {
    const classNames = [...element.classList];
    const elementId = element.id;
    const href = element.href;
    const innerHTML = element.innerHTML;
    const currentPageTitle = document.title;

    const onClick = (e: React.MouseEvent<HTMLAnchorElement>) => {
        e.preventDefault();
        e.stopPropagation();
        window.history.pushState({}, currentPageTitle, href);
    };

    const parentElement = element.parentElement;

    parentElement.innerHTML = "";

    return ReactDOM.createPortal(
        <a
            className={classNames.join(" ")}
            href={href}
            onClick={onClick}
            id={elementId}
            dangerouslySetInnerHTML={{ __html: innerHTML }}
        />,
        parentElement
    );
};

export const AsyncSearchResultsBox = ({ }) => {
    // get all elements with data-enhance="pagination"

    // const [requestCounter, setRequestCounter] = useState(0)

    let requestCounter: number = 0;

    const paginationElements = document.querySelectorAll(
        "[data-enhance=pagination-link]"
    );
    // get search filters submit button
    const searchFiltersSubmitButton = document.querySelector(
        "[data-enhance=search-filters-submit]"
    );

    const updateSearchResults = async (
        submitURL: string,
        requestCounterCheck: number
    ) => {
        const searchResultsContainer = document.querySelector(
            "#search-results-container"
        );
        searchResultsContainer.innerHTML = "Loading...";
        const response = await fetch(submitURL);
        const responseText = await response.text();
        const tempElement = document.createElement("html");
        tempElement.innerHTML = responseText;
        const searchResults = tempElement.querySelector(
            "#search-results-container"
        );

        const currentURLQuerystring = document.location.search;
        if (requestCounterCheck !== requestCounter) {
            return;
        }

        searchResultsContainer.innerHTML = searchResults.innerHTML;
    };

    const handleChange = async () => {
        const currentURLQuerystring = document.location.search;

        const form = document.querySelector<HTMLFormElement>(
            "#search-filters-form"
        );

        const formData = new FormData(
            document.querySelector("#search-filters-form") as HTMLFormElement
        );
        const queryString = new URLSearchParams(formData as any).toString();


        if (currentURLQuerystring == `?${queryString}`) {
            return;
        }

        requestCounter += 1;

        const formAction = form.action;
        const path = formAction.split("?")[0];
        const submitURL = `${path}?${queryString}`;
        window.history.pushState({}, document.title, submitURL);

        const requestCounterCheck = requestCounter;
        await updateSearchResults(submitURL, requestCounterCheck);
    };

    document.addEventListener("change", async (e) => {
        handleChange();
    });

    const formFieldsContainer = document.querySelector("#search-form-fields");
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            const oldValue = mutation.oldValue;
            const newValue = mutation.target.textContent;
            if (oldValue !== newValue) {
                handleChange();
            }
        });
    });
    observer.observe(formFieldsContainer, {
        characterDataOldValue: true,
        subtree: true,
        childList: true,
        characterData: true,
    });

    document.querySelector(".filter-items").addEventListener("submit", (e) => {
        e.preventDefault();
    });

    const applyFiltersButton = document.querySelector("#apply-filters-button");
    applyFiltersButton.style.display = "none";

    return (
        <div>
            {[...paginationElements].map((element) => (
                <AnchorElementPortal element={element as HTMLElement} />
            ))}
        </div>
    );
};

export const renderAsyncSearchResults = () => {
    const rootContainer = document.createElement("div");
    rootContainer.id = "async-search-results";

    ReactDOM.render(<AsyncSearchResultsBox />, rootContainer);
};
