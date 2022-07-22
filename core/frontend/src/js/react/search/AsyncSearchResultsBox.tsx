import React, { useEffect } from "react";
import ReactDOM from "react-dom";

interface AnchorElementPortalProps {
    element: HTMLElement;
}
const AnchorElementPortal = ({element}) => {
    const classNames = [...element.classList];
    const elementId = element.id;
    const href = element.href;
    const innerHTML = element.innerHTML;
    const currentPageTitle = document.title;

    const onClick = (e: React.MouseEvent<HTMLAnchorElement>) => {
        e.preventDefault();
        e.stopPropagation();
        window.history.pushState({}, currentPageTitle, href);
    }

    const parentElement = element.parentElement;

    parentElement.innerHTML = ""

    return ReactDOM.createPortal(
        <a className={classNames.join(" ")} href={href} onClick={onClick} id={elementId} dangerouslySetInnerHTML={{__html: innerHTML}} />,
        parentElement
    )
}

const getFormData = (formId: string) => {
    const formData = new FormData();
    const inputElements = document.querySelectorAll<HTMLInputElement>(`${formId} input`);
    const selectElements = document.querySelectorAll<HTMLSelectElement>(`${formId} select`);
    const textareaElements = document.querySelectorAll<HTMLTextAreaElement>(`${formId} textarea`);

    // iterate over elements and add to formData
    inputElements.forEach(inputElement => {
        if(inputElement.value){
            formData.append(inputElement.name, inputElement.value);
        }
    })
    selectElements.forEach(selectElement => {
        if(!selectElement.value) return
        formData.append(selectElement.name, selectElement.value);
    })
    textareaElements.forEach(textareaElement => {
        if(!textareaElement.value) return
        formData.append(textareaElement.name, textareaElement.value);
    })
    return formData;
}

export const AsyncSearchResultsBox = ({}) => {

    // get all elements with data-enhance="pagination"
    const paginationElements = document.querySelectorAll("[data-enhance=pagination-link]");
    // get search filters submit button
    const searchFiltersSubmitButton = document.querySelector("[data-enhance=search-filters-submit]");

    const updateSearchResults = async (submitURL: string) => {
        const searchResultsContainer = document.querySelector("#search-results-container");
        searchResultsContainer.innerHTML = "Loading...";
        const response = await fetch(submitURL);
        const responseText = await response.text();
        const tempElement = document.createElement("html");
        tempElement.innerHTML = responseText;
        const searchResults = tempElement.querySelector("#search-results-container");
        searchResultsContainer.innerHTML = searchResults.innerHTML;
    }

    document.addEventListener("change", async (e) => {

        const form = document.querySelector<HTMLFormElement>("#search-filters-form");

        const formData =  new FormData(document.querySelector("#search-filters-form") as HTMLFormElement)
        const queryString = new URLSearchParams(formData as any).toString();
        const formAction = form.action;
        const path = formAction.split("?")[0];
        const submitURL = `${path}?${queryString}`;
        window.history.pushState({}, document.title, submitURL);
        await updateSearchResults(submitURL);

    })

    document.querySelector(".filter-items").addEventListener("submit", (e) => {
        e.preventDefault();
    })

    console.log("paginationElements", paginationElements);
    return <div>
        {[...paginationElements].map((element) => <AnchorElementPortal element={element as HTMLElement} />)}
    </div>
}

export const renderAsyncSearchResults = () => {
    const container = document.getElementById("search-results-container");

    const rootContainer = document.createElement("div");
    rootContainer.id = "async-search-results";

    ReactDOM.render(<AsyncSearchResultsBox />, rootContainer);
}
