import React, { useEffect, useState } from "react";

function CompaniesForm(props) {
    // Setup variables to contain data/information
    const [searchTerm, setSearchTerm] = useState("");
    const [companiesList, setCompaniesList] = useState([]);
    const [selectedCompany, setSelectedCompany] = useState({});
    const [selectedCompaniesList, setSelectedCompaniesList] = useState([]);
    const [unrecognisedCompany, setUnrecognisedCompany] = useState("");
    const [addedCompaniesList, setAddedCompaniesList] = useState([]);

    // Variables to decide what elements to display
    const [showSearchBox, setShowSearchBox] = useState(true);
    const [showCompanyList, setShowCompanyList] = useState(false);
    const [showCompanyDetails, setShowCompanyDetails] = useState(false);
    const [showSelectedList, setShowSelectedList] = useState(false);
    const [showAddCompanySection, setShowAddCompanySection] = useState(false);

    // Setup identifying the Django hidden input element
    const hiddenDjangoInput = document.getElementById(
        "barrier-companies-affected-input"
    );
    const hiddenDjangoInputUnrecognised = document.getElementById(
        "id_barrier-companies-affected-unrecognised_company"
    );

    // Make unrecognised country input hidden for when JS is enabled
    const unrecognisedCompanyDjango = document.getElementById(
        "barrier-unknown-company-section"
    );
    unrecognisedCompanyDjango.classList.add("govuk-visually-hidden");

    // Onclick event for search button - calls async method to get companies data
    const searchCompany = (event) => {
        var inputSearchTerm = document.getElementById("companies-search");
        setSearchTerm(inputSearchTerm.value);
        callCompaniesHouse(inputSearchTerm.value);
    };

    // Onclick event for company information cards - hides elements & displays specific company details
    const displayCompanyDetails = (company) => {
        // Change sections being displayed
        setShowSearchBox(false);
        setShowCompanyList(false);
        setShowCompanyDetails(true);

        // Set the selected company state to the clicked-on company
        setSelectedCompany(company);
    };

    // Onclick event for search again button - hides display and unhides search sections
    const searchAgain = (event) => {
        // Change sections being displayed
        setShowSearchBox(true);
        setShowCompanyList(true);
        setShowCompanyDetails(false);
    };

    // Onclick event for add company button - updates selected companies list & hidden input field
    const addCompany = (event) => {
        // Update the list of selected companies
        let updatedSelectionList = selectedCompaniesList;
        updatedSelectionList.push(selectedCompany);
        setSelectedCompaniesList(updatedSelectionList);

        // Update Django hidden input value
        hiddenDjangoInput.value = JSON.stringify(selectedCompaniesList);

        // Change sections being displayed
        setShowCompanyDetails(false);
        setShowSelectedList(true);
    };

    const addUnrecognisedCompany = (event) => {
        // Update the list of added companies
        let updatedAddedCompaniesList = addedCompaniesList;
        updatedAddedCompaniesList.push(unrecognisedCompany);
        setAddedCompaniesList(updatedAddedCompaniesList);

        // Update Django hidden input value
        hiddenDjangoInputUnrecognised.value =
            JSON.stringify(addedCompaniesList);

        // Change sections being displayed
        setShowSelectedList(true);
        setShowSearchBox(false);
        setShowCompanyList(false);
        setShowAddCompanySection(false);
    };

    // Onclick event for remove company button (on a searched company) - updates selected companies list & hidden input field
    const removeCompany = (company) => {
        // Update the list of selected companies
        let updatedSelectionList = selectedCompaniesList;
        const index = updatedSelectionList.indexOf(company);
        updatedSelectionList.splice(index, 1);
        setSelectedCompaniesList(updatedSelectionList);

        // Update Django hidden input value
        hiddenDjangoInput.value = JSON.stringify(selectedCompaniesList);

        // Remove list entry of removed company
        const companyListElement = document.getElementById(
            company.company_number
        );
        companyListElement.remove();

        // If all elements are removed, show the default search bar instead of the list
        if (selectedCompaniesList.length < 1 && addedCompaniesList.length < 1) {
            setShowSelectedList(false);
            setShowSearchBox(true);
        }
    };

    // Onclick event for remove company button (on an added company) - updates selected companies list & hidden input field
    const removeAddedCompany = (company) => {
        // Update the list of selected companies
        let updatedSelectionList = addedCompaniesList;
        const index = updatedSelectionList.indexOf(company);
        updatedSelectionList.splice(index, 1);
        setAddedCompaniesList(updatedSelectionList);

        // Update Django hidden input value
        hiddenDjangoInputUnrecognised.value =
            JSON.stringify(addedCompaniesList);

        // Remove list entry of removed company
        // TODO:
        // This should be automatically updated via React, need to get this to work ractively rather than manually amending page.
        const companyListElement = document.getElementById(company);
        companyListElement.remove();

        // If all elements are removed, show the default search bar instead of the list
        if (selectedCompaniesList.length < 1 && addedCompaniesList.length < 1) {
            setShowSelectedList(false);
            setShowSearchBox(true);
        }
    };

    // Onclick event for add another company button - hides/displays elements
    const addAnotherCompany = (event) => {
        // Change sections being displayed
        setShowSearchBox(true);
        setShowSelectedList(false);
    };

    // Onclick event for cancel search button - hides/displays elements
    const cancelSearch = (event) => {
        // Change sections being displayed
        setShowSearchBox(false);
        setShowCompanyList(false);
        setShowAddCompanySection(false);
        setShowSelectedList(true);
    };

    // Async function - calls django view wrapper which will call companies house
    async function callCompaniesHouse(searchTerm) {
        const url = "/companies/search/" + searchTerm + "/";
        const response = await fetch(url, {
            headers: {
                "X-Requested-With": "XMLHttpRequest",
            },
        })
            .then((res) => res.json())
            .then((result) => {
                setCompaniesList(result);
                // If there are no results, show the add company blox
                if (result.length < 1) {
                    setShowAddCompanySection(true);
                } else {
                    setShowAddCompanySection(false);
                }
            })
            .then(() => {
                setShowCompanyList(true);
            });
    }

    // Use effect hook to set initial state of react component - in case returning to form from
    // other pages. Passing empty array to useEffect means it will run once on page load.
    useEffect(() => {
        var passedInputCompanies = [];
        if (hiddenDjangoInput.value != "None") {
            passedInputCompanies = JSON.parse(hiddenDjangoInput.value);
            if (passedInputCompanies != []) {
                setSelectedCompaniesList(passedInputCompanies);
            }
        }
        var passedAddedCompanies = [];
        if (hiddenDjangoInputUnrecognised.value) {
            passedAddedCompanies = JSON.parse(
                hiddenDjangoInputUnrecognised.value
            );
            if (passedAddedCompanies != []) {
                setAddedCompaniesList(passedAddedCompanies);
            }
        }
        if (
            passedInputCompanies.length > 0 ||
            passedAddedCompanies.length > 0
        ) {
            setShowSearchBox(false);
            setShowSelectedList(true);
        }
    }, []);

    return (
        <div>
            {showSearchBox ? (
                <div
                    id="companies-search-bar-section"
                    className="govuk-form-group"
                >
                    <label className="govuk-label govuk-label--s">
                        {props.searchLabel}
                    </label>
                    <span className="govuk-hint">{props.searchHelpText}</span>
                    <div className="search-form__input-group">
                        <input
                            id="companies-search"
                            className="govuk-input search-form__input"
                            name="companies-search"
                            type="text"
                        />
                        <div
                            id="search-companies-button"
                            className="search-form__button govuk-button"
                            onClick={searchCompany}
                        >
                            Search
                        </div>
                    </div>
                    {selectedCompaniesList.length > 0 ||
                    addedCompaniesList.length > 0 ? (
                        <div
                            id="cancel-search-companies-button"
                            className="govuk-link"
                            onClick={cancelSearch}
                        >
                            Cancel
                        </div>
                    ) : null}
                </div>
            ) : null}

            {showCompanyList ? (
                <div id="companies-list-section" className="govuk-form-group">
                    <h2 className="results-count" role="alert">
                        <span className="results-count__number">
                            {companiesList.length}
                        </span>
                        <span> companies match </span>
                        <span className="highlight">{searchTerm}</span>
                    </h2>
                    <ul className="search-card-list">
                        {companiesList &&
                            companiesList.map((company) => (
                                <li
                                    className="search-card"
                                    key={company.company_number}
                                >
                                    <a
                                        className="search-card__link"
                                        onClick={(event) =>
                                            displayCompanyDetails(company)
                                        }
                                    >
                                        <h3 className="search-card__heading">
                                            {company.title}
                                        </h3>
                                        <dl className="search-card__values">
                                            {company.company_number ? (
                                                <span>
                                                    <dt className="search-card__values__key">
                                                        Companies House number
                                                    </dt>
                                                    <dd className="search-card__values__value">
                                                        {" "}
                                                        {company.company_number}
                                                    </dd>
                                                </span>
                                            ) : null}
                                            {company.title ? (
                                                <span>
                                                    <dt className="search-card__values__key">
                                                        Companies Name
                                                    </dt>
                                                    <dd className="search-card__values__value">
                                                        {" "}
                                                        {company.title}
                                                    </dd>
                                                </span>
                                            ) : null}
                                            {company.date_of_creation ? (
                                                <span>
                                                    <dt className="search-card__values__key">
                                                        Incorporated on
                                                    </dt>
                                                    <dd className="search-card__values__value">
                                                        {" "}
                                                        {
                                                            company.date_of_creation
                                                        }
                                                    </dd>
                                                </span>
                                            ) : null}
                                            {company.date_of_cessation ? (
                                                <span>
                                                    <dt className="search-card__values__key">
                                                        Terminated on
                                                    </dt>
                                                    <dd className="search-card__values__value">
                                                        {" "}
                                                        {
                                                            company.date_of_cessation
                                                        }
                                                    </dd>
                                                </span>
                                            ) : null}
                                            {company.address_snippet ? (
                                                <span>
                                                    <dt className="search-card__values__key">
                                                        Primary address
                                                    </dt>
                                                    <dd className="search-card__values__value">
                                                        {" "}
                                                        {
                                                            company.address_snippet
                                                        }
                                                    </dd>
                                                </span>
                                            ) : null}
                                        </dl>
                                    </a>
                                </li>
                            ))}
                    </ul>
                </div>
            ) : null}

            {showAddCompanySection ? (
                <div
                    id="add-unrecognised-company-section"
                    className="govuk-form-group govuk-cookie-banner govuk-!-padding-5"
                >
                    <label className="govuk-label govuk-label--s">
                        Can&apos;t find the company?
                    </label>
                    <span className="govuk-hint">
                        If you can&apos;t find the company or organisation
                        you&apos;re looking for, try a different search query,
                        check the company&apos;s website or any email
                        correspondence that contains company registration
                        details.
                    </span>
                    <div id="or-add-text" className="govuk-label--s">
                        Or
                    </div>
                    <label className="govuk-label govuk-label--s">
                        Add a company
                    </label>
                    <input
                        id="add-unrecognised-company-input"
                        className="govuk-input govuk-!-width-one-half"
                        name="add-unrecognised-company-input"
                        type="text"
                        onChange={(event) =>
                            setUnrecognisedCompany(event.target.value)
                        }
                    />
                    <div
                        id="add-companies-button"
                        className="search-form__button govuk-button govuk-!-margin-0"
                        onClick={addUnrecognisedCompany}
                    >
                        Add company
                    </div>
                </div>
            ) : null}

            {showCompanyDetails ? (
                <div id="company-details-section" className="govuk-form-group">
                    <h2 className="govuk-heading-s">Company details</h2>
                    <dl className="details-list">
                        {selectedCompany["title"] ? (
                            <div className="details-list__group">
                                <dt className="details-list__key">
                                    Registered name
                                </dt>
                                <dd className="details-list__value">
                                    {selectedCompany["title"]}
                                </dd>
                            </div>
                        ) : null}
                        {selectedCompany["company_number"] ? (
                            <div className="details-list__group">
                                <dt className="details-list__key">
                                    Companies House number
                                </dt>
                                <dd className="details-list__value">
                                    {selectedCompany["company_number"]}
                                </dd>
                            </div>
                        ) : null}
                        {selectedCompany["address_snippet"] ? (
                            <div className="details-list__group">
                                <dt className="details-list__key">
                                    Primary address
                                </dt>
                                <dd className="details-list__value">
                                    {selectedCompany["address_snippet"]}
                                </dd>
                            </div>
                        ) : null}
                        {selectedCompany["sic_codes"] ? (
                            <div className="details-list__group">
                                <dt className="details-list__key">Sector</dt>
                                <dd className="details-list__value">
                                    {selectedCompany["sic_codes"]}
                                </dd>
                            </div>
                        ) : null}
                        {selectedCompany["date_of_creation"] ? (
                            <div className="details-list__group">
                                <dt className="details-list__key">
                                    Incorporated on
                                </dt>
                                <dd className="details-list__value">
                                    {selectedCompany["date_of_creation"]}
                                </dd>
                            </div>
                        ) : null}
                    </dl>
                    <div
                        id="add-company-button"
                        className="search-form__button govuk-button"
                        onClick={addCompany}
                    >
                        Add company
                    </div>
                    <div id="or-text" className="govuk-label--s">
                        Or
                    </div>
                    <div
                        id="search-again-button"
                        className="govuk-link"
                        onClick={searchAgain}
                    >
                        Search again
                    </div>
                </div>
            ) : null}

            {showSelectedList ? (
                <div
                    id="selected-companies-section"
                    className="govuk-form-group"
                >
                    <div
                        id="selected-companies-list"
                        className="selection-list restrict-width"
                    >
                        <h3 className="selection-list__heading">
                            Selected companies
                        </h3>
                        <ul className="selection-list__list">
                            {selectedCompaniesList &&
                                selectedCompaniesList.map((company) => (
                                    <li
                                        id={company.company_number}
                                        className="selection-list__list__item"
                                        key={company.company_number}
                                    >
                                        <span>{company.title}</span>
                                        <span
                                            id="remove-company-button"
                                            className="selection-list__list__item__remove-form__submit"
                                            onClick={(event) =>
                                                removeCompany(company)
                                            }
                                        >
                                            remove
                                        </span>
                                    </li>
                                ))}
                            {addedCompaniesList &&
                                addedCompaniesList.map((company) => (
                                    <li
                                        id={company}
                                        className="selection-list__list__item"
                                        key={company}
                                    >
                                        <span>{company}</span>
                                        <span
                                            id="remove-company-button"
                                            className="selection-list__list__item__remove-form__submit"
                                            onClick={(event) =>
                                                removeAddedCompany(company)
                                            }
                                        >
                                            remove
                                        </span>
                                    </li>
                                ))}
                            <div
                                id="add-another-company-button"
                                className="govuk-button button--secondary selection-list__add-button"
                                onClick={addAnotherCompany}
                            >
                                Add another company
                            </div>
                        </ul>
                    </div>
                </div>
            ) : null}
        </div>
    );
}

export default CompaniesForm;
