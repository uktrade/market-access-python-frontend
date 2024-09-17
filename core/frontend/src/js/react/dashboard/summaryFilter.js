import React, {useEffect, useState} from "react";
import { render } from "react-dom";

const SummaryCard = ({value, description, url, search_params}) => {

    const handleSearchParam = () => {
        return `${url}?${search_params}`;
    };

    return (
        <div className="govuk-grid-column-one-third">
            <div className="govuk-inset-text summary-card">
                <p>
                    <span className="govuk-heading-xl">{value}</span> {description}
                </p>
                <div className="summary-card__data-link">
                    <a href={handleSearchParam()}>See the barriers</a>
                </div>
            </div>
        </div>
    );
}

const SummaryCards = () => {

    const form = document.querySelector("#filters-form");

    const remove_hidden = false;

    const applyFiltersButton = document.querySelector("#apply-filters-button");

    useEffect(() => {
        const handleApplyFilters = async (/** @type {{ preventDefault: () => void; }} */ event) => {
            event.preventDefault();
            const params = getSearchParamsFromForm();
            await fetchData(params);
        };

        if (applyFiltersButton) {
            applyFiltersButton.addEventListener("click", handleApplyFilters);
        }

        return () => {
            if (applyFiltersButton) {
                applyFiltersButton.removeEventListener("click", handleApplyFilters);
            }
        };
    }, []);

    const [data, setData] = useState(null);

    const [filters, setFilters] = useState([]);

    /**
     * Fetches data from the server based on the provided query parameters.
     * 
     * @param {string} queryParams - The query parameters to be included in the request URL.
     * @returns {Promise<void>} - A promise that resolves when the data is fetched and set.
     */
    const fetchData = async (queryParams) => {
    
        // update the current URL with the new query params
        const searchParams = new URLSearchParams(queryParams);
        window.history.pushState({}, "", `?${searchParams.toString()}`);

        const url = queryParams ? `/dashboard-summary/?${queryParams}` : "/dashboard-summary/";
        const response = await fetch(url, {
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "Content-Type": "application/json",
            },
        });
        const data = await response.json();
        setData(data);
    };

    const getSearchParamsFromForm = () => {
        // @ts-ignore
        const formData = new FormData(form);
        // @ts-ignore
        return new URLSearchParams(formData).toString();
    };

    const parseIso = (/** @type {string | number | Date} */ dateString) => {
        const date = new Date(dateString);
        return new Date(date).toLocaleDateString("en-GB", {
            day: "numeric",
            month: "long",
            year: "numeric"
        });
    }
    
    useEffect(() => {
        fetchData("");
    }, []);

    useEffect(() => {
        // set filters to be used in the summary cards
        const searchParams = new URLSearchParams(window.location.search);
        const params = Object.fromEntries(searchParams.entries());
        const filters = Object.keys(params).map((key) => {
            return {
                label: key,
                value: params[key],
                readable_value: params[key],
                remove_url: searchParams.toString().replace(`${key}=${params[key]}`, ""),
            };
        });
        setFilters(filters);
    }, [window.location.search]);


    return (
        <>
            <h3 className="govuk-summary-card__title">Summary data</h3>
            <div className="p-l-3" id="active filters">
                <ul className="govuk-list">
                    {filters.map((filter, index) => (
                        filter.value && (
                            <li className="active-filters__item" key={index}>
                                {remove_hidden ? (
                                    <>
                                        <h4 className="active-filter__heading">{filter.label}:</h4>
                                        <p className="active-filter__text">{filter.readable_value.replace(/<\/?[^>]+(>|$)/g, "")}</p>
                                    </>
                                ) : (
                                    <a
                                        href={filter.remove_url ? `?${filter.remove_url}` : '/barriers/search'}
                                        className="active-filters__item__link"
                                        title={`Remove ${filter.label} filter`}
                                    >
                                        <h4 className="active-filter__heading">{filter.label}:</h4>
                                        <p className="active-filter__text">{filter.readable_value.replace(/<\/?[^>]+(>|$)/g, "")}</p>
                                        <span className="sr-only govuk-visually-hidden">
                                            Activate link to remove {filter.label} filter with value open quote {filter.readable_value.replace(/<\/?[^>]+(>|$)/g, "")} end quote.
                                        </span>
                                    </a>
                                )}
                            </li>
                        )
                    ))}
                </ul>
            </div>
            <div className="govuk-grid-row">
                <h3 className="govuk-summary-card__title p-l-3">Open barriers</h3>
                <SummaryCard
                    value={data && data.barriers.open}
                    description="barriers are open."
                    url="{% url 'barriers:search' %}"
                    search_params={getSearchParamsFromForm()}
                />
                <SummaryCard
                    value={data && data.barriers.pb100}
                    description="PB100 barriers are open."
                    url="{% url 'barriers:search' %}"
                    search_params={`${getSearchParamsFromForm()}&combined_priority=APPROVED`}
                />
                <SummaryCard
                    value={data && data.barriers.overseas_delivery}
                    description="Overseas delivery barriers are open."
                    url="{% url 'barriers:search' %}"
                    search_params={getSearchParamsFromForm()}
                />
            </div>
            <div className="govuk-grid-row">
                <h3 className="govuk-summary-card__title p-l-3">
                    {`Barriers which have been resolved or are projected to be resolved between ${parseIso(data && data.financial_year.current_start)} and ${parseIso(data && data.financial_year.current_end)} current financial year`}.
                </h3>
                <SummaryCard
                    value={data && data.barriers_current_year.open}
                    description="barriers have been resolved in the current financial year."
                    url="{% url 'barriers:search' %}"
                    search_params={getSearchParamsFromForm()}
                />
                <SummaryCard
                    value={data && data.barriers_current_year.pb100}
                    description="PB100 barriers are estimated to be resolved in the current financial year."
                    url="#"
                    search_params=""
                />
                <SummaryCard
                    value={data && data.barriers_current_year.overseas_delivery}
                    description="Overseas delivery barriers are estimated to be resolved in the current financial year."
                    url="#"
                    search_params=""
                />
            </div>
        </>
    );
}

const renderSummaryCards = (/** @type {string} */ elementId) => {
    const element = document.getElementById(elementId);
    render(
        <SummaryCards
        />,
        element
    );
}

export default renderSummaryCards;
