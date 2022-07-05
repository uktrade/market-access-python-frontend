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

    // useEffect(() => {
    //     parentElement.innerHTML = ""
    // }, [])


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
            // debugger;
            // console.log("input", inputElement.value);
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
        applyListnersToPaginationElements()
    }

    const applyListnersToPaginationElements = () => {
        // document.querySelectorAll<HTMLAnchorElement>("[data-enhance=pagination-link]").forEach(paginationElement => {
        //     paginationElement.addEventListener("click", async (e) => {
        //         e.preventDefault();
        //         e.stopPropagation();
        //         const submitURL = paginationElement.href;
        //         await updateSearchResults(submitURL);
        //     }
        //     )
        // })
    }
    applyListnersToPaginationElements();

    document.addEventListener("change", async (e) => {
        // console.log("change event detected", e)
        // console.log("form data", getFormData("#search-filters-form"))

        const form = document.querySelector<HTMLFormElement>("#search-filters-form");

        const formData =  new FormData(document.querySelector("#search-filters-form") as HTMLFormElement)
        const queryString = new URLSearchParams(formData as any).toString();
        // console.log("vanilla form data", [...formData.entries()])
        // console.log("query string", queryString)
        const formAction = form.action;
        const path = formAction.split("?")[0];
        const submitURL = `${path}?${queryString}`;
        window.history.pushState({}, document.title, submitURL);
        // console.log("submit url", submitURL)
        await updateSearchResults(submitURL);

    })

    document.querySelector(".filter-items").addEventListener("submit", (e) => {
        e.preventDefault();
        console.log("form submit event detected",e)
        console.log("form data", getFormData("#search-filters-form"))
    })

    console.log("paginationElements", paginationElements);
    return <div>
        {[...paginationElements].map((element) => <AnchorElementPortal element={element as HTMLElement} />)}
    </div>
}

export const renderAsyncSearchResults = () => {
    const container = document.getElementById("search-results-container");

    // create an element with id "async-search-results"
    const rootContainer = document.createElement("div");
    rootContainer.id = "async-search-results";

    ReactDOM.render(<AsyncSearchResultsBox />, rootContainer);
}
