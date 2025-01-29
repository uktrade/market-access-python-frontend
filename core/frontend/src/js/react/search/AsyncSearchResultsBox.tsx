import React, {useEffect} from "react";
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

/**
 * Renders the asynchronous search results box.
 * This component handles updating the search results based on user input and filters.
 */
export const AsyncSearchResultsBox = (): JSX.Element => {
    let requestCounter = 0;

    useEffect(() => {
        const searchResultsContainer = document.querySelector("#search-results-container");
        const form = document.querySelector<HTMLFormElement>("#search-filters-form");

        if (!searchResultsContainer || !form) return;

        const updateSearchResults = async (submitURL: string, requestCounterCheck: number): Promise<void> => {
            searchResultsContainer.innerHTML = "Loading...";
            const response = await fetch(submitURL);
            const responseText = await response.text();
            const tempElement = document.createElement("html");
            tempElement.innerHTML = responseText;
            const searchResults = tempElement.querySelector("#search-results-container");

            if (requestCounterCheck === requestCounter && searchResults) {
                searchResultsContainer.innerHTML = searchResults.innerHTML;
            }
        };

        const handleChange = async (): Promise<void> => {
            const currentURLQuerystring = document.location.search;
            const formData = new FormData(form);
            const queryString = new URLSearchParams(formData as any).toString();

            if (currentURLQuerystring === queryString) return;

            requestCounter += 1;
            const formAction = form.action.split("?")[0];
            const submitURL = `${formAction}?${queryString}`;
            window.history.pushState({}, document.title, submitURL);

            await updateSearchResults(submitURL, requestCounter);
        };

        document.addEventListener("change", handleChange);

        const formFieldsContainer = document.querySelector("#search-form-fields");
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList') {
                    if (mutation.oldValue !== mutation.target.textContent) {
                        const value = mutation.target.textContent;
                        // Only trigger handleChange if the value is not empty
                        if (value && value.length > 0) {
                            handleChange();
                        }
                    }
                }
            });
        });

        if (formFieldsContainer) {
            observer.observe(formFieldsContainer, {
                characterData: false,
                childList: true,
                subtree: false,
                attributes: false,
                characterDataOldValue: true
            });
        }

        const filterItemsForm = document.querySelector(".filter-items");
        if (filterItemsForm) {
            filterItemsForm.addEventListener("submit", (e) => e.preventDefault());
        }

        const applyFiltersButton = document.querySelector<HTMLElement>("#apply-filters-button");
        if (applyFiltersButton) {
            applyFiltersButton.style.display = "none";
        }

        return () => {
            document.removeEventListener("change", handleChange);
            observer.disconnect();
        };
    }, []);

    const paginationElements = document.querySelectorAll("[data-enhance=pagination-link]");
    return (
        <>
            {Array.from(paginationElements).map((element) => (
                <AnchorElementPortal key={element.id} element={element as HTMLElement} />
            ))}
        </>
    );
};

export const renderAsyncSearchResults = (): void => {
    const rootContainer = document.createElement("div");
    rootContainer.id = "async-search-results";

    ReactDOM.render(<AsyncSearchResultsBox />, rootContainer);
};
