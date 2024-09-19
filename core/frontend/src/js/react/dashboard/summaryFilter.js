import React, { useEffect, useState } from "react";
import { render } from "react-dom";

import { getCheckboxValues } from "../utils";
import { BARRIER_STATUS } from "../constants";

/**
 * Renders a summary card component.
 * @param {Object} props - The component props.
 * @param {string} props.value - The value to be displayed in the card.
 * @param {string} props.description - The description to be displayed in the card.
 * @param {string} props.url - The URL to link to.
 * @param {string} props.search_params - The search parameters to be included in the URL.
 * @returns {JSX.Element} - The rendered summary card component.
 */
const SummaryCard = ({ value, description, url, search_params }) => {
    const handleSearchParam = () => {
        return `${url}?${search_params}`;
    };

    return (
        <div className="govuk-grid-column-one-third">
            <div className="govuk-inset-text summary-card">
                <p>
                    <span className="govuk-heading-xl">{value}</span>{" "}
                    {description}
                </p>
                <div className="summary-card__data-link">
                    <a href={handleSearchParam()}>See the barriers</a>
                </div>
            </div>
        </div>
    );
};

/**
 *
 * @param {*} htmlElement
 * @returns {Object} - label and options
 */
const getOptionValue = (htmlElement) => {
    const label = htmlElement.querySelector("legend").textContent.trim();
    const options = getCheckboxValues(htmlElement);
    return { label, options };
};

/**
 * Renders the summary cards component & filters.
 *
 * @param {Object} props - The component props.
 * @param {Object} props.filterValues - The filter values.
 * @returns {JSX.Element} - The rendered summary cards component.
 */
const SummaryCards = ({ filterValues }) => {
    const form = document.querySelector("#filters-form");

    const remove_hidden = true;

    const applyFiltersButton = document.querySelector("#apply-filters-button");

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

        const searchParamsWithLocation = addLocation(searchParams);

        window.history.pushState(
            {},
            "",
            `?${searchParamsWithLocation.toString()}`,
        );

        const url = searchParamsWithLocation
            ? `/dashboard-summary/?${searchParamsWithLocation.toString()}`
            : "/dashboard-summary/";
        const response = await fetch(url, {
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "Content-Type": "application/json",
            },
        });
        const data = await response.json();
        setData(data);
    };

    const formatAdminAreas = (searchParams) => {
        const admin_areas = [];
        if (searchParams.get("admin_areas")) {
            const adminAreasData = JSON.parse(searchParams.get("admin_areas"));
            for (const key in adminAreasData) {
                const values = adminAreasData[key];
                for (const admin_area_id of values) {
                    admin_areas.push(admin_area_id);
                }
            }
        }
        return admin_areas;
    };

    const addLocation = (queryParams) => {
        // update the current URL with the new query params
        const searchParams = new URLSearchParams(queryParams);

        const adminAreas = formatAdminAreas(searchParams);

        if (adminAreas.length > 0) {
            searchParams.append(
                "admin_areas",
                adminAreas.filter(Boolean).join(","),
            );
        } else {
            searchParams.delete("admin_areas");
        }

        // Get all country, region, and country_trading_bloc values
        const locationParams = [
            ...searchParams.getAll("country"), // Get all 'country' values
            searchParams.get("region"), // Get 'region'
            searchParams.get("country_trading_bloc"), // Get 'country_trading_bloc'
        ]
            .filter(Boolean)
            .join(","); // Filter out empty values and join with commas

        // Remove 'country', 'region', and 'country_trading_bloc' parameters
        searchParams.delete("country");
        searchParams.delete("region");
        searchParams.delete("country_trading_bloc");

        // Add the new 'location' parameter if there are any valid values
        if (locationParams) {
            searchParams.append("location", locationParams);
        }

        // Return the updated searchParams object
        return searchParams;
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
            year: "numeric",
        });
    };

    const getReadableValue = (
        /** @type {string} */ value,
        /** @type {string} */ type,
    ) => {
        if (type === "sector") {
            return filterValues.sector.find((sector) => sector.value === value)
                .label;
        } else if (type === "policy_team") {
            return filterValues.policy_team.find(
                (policy_team) => policy_team.value === value,
            ).label;
        } else if (type === "location") {
            // check if value is comma separated then split it and return an array
            if (value.includes(",")) {
                return value
                    .split(",")
                    .map(
                        (val) =>
                            filterValues.location.find(
                                (location) => location.value === val,
                            ).label,
                    );
            } else {
                return filterValues.location.find(
                    (location) => location.value === value,
                ).label;
            }
        } else if (type === "status") {
            return BARRIER_STATUS[value];
        }
        return value;
    };

    useEffect(() => {
        const handleApplyFilters = async (
            /** @type {{ preventDefault: () => void; }} */ event,
        ) => {
            event.preventDefault();
            const params = getSearchParamsFromForm();
            await fetchData(params);
        };

        if (applyFiltersButton) {
            applyFiltersButton.addEventListener("click", handleApplyFilters);
        }

        return () => {
            if (applyFiltersButton) {
                applyFiltersButton.removeEventListener(
                    "click",
                    handleApplyFilters,
                );
            }
        };
    }, []);

    useEffect(() => {
        fetchData("status=2");
    }, []);

    useEffect(() => {
        // set filters to be used in the summary cards
        const searchParams = new URLSearchParams(window.location.search);
        const params = {};

        // Use forEach to handle duplicate keys
        searchParams.forEach((value, key) => {
            if (!params[key]) {
                params[key] = [];
            }
            params[key].push(value);
        });

        // Build filters array
        const filters = Object.keys(params)
            .map((key) => {
                const values = params[key];
                return values.map((val) => ({
                    label: key,
                    value: val,
                    readable_value: val && getReadableValue(val, key),
                    remove_url: new URLSearchParams(
                        [...searchParams].filter(
                            ([paramKey, paramValue]) =>
                                !(paramKey === key && paramValue === val),
                        ),
                    ).toString(),
                }));
            })
            .flat();

        setFilters(filters);
    }, [window.location.search]);

    return (
        <>
            <h3 className="govuk-summary-card__title">Summary data</h3>
            <div className="p-l-3" id="active filters">
                <ul className="govuk-list">
                    {Object.entries(
                        // if the filter label is location then convert to individual location values
                        filters
                            .map((filter) => {
                                // set filters to be used in the summary cards
                                const searchParams = new URLSearchParams(
                                    window.location.search,
                                );
                                if (filter.label === "location") {
                                    return filter.value
                                        .split(",")
                                        .map((val) => ({
                                            label: filter.label,
                                            value: val,
                                            readable_value:
                                                val &&
                                                getReadableValue(
                                                    val,
                                                    filter.label,
                                                ),
                                            remove_url: new URLSearchParams(
                                                [...searchParams].filter(
                                                    ([paramKey, paramValue]) =>
                                                        !(
                                                            paramKey ===
                                                                filter.label &&
                                                            paramValue === val
                                                        ),
                                                ),
                                            ).toString(),
                                        }));
                                }
                                return filter;
                            })
                            .flat()
                            .reduce((acc, filter) => {
                                if (filter.value) {
                                    // Group filters by label, appending values under the same label
                                    if (!acc[filter.label]) {
                                        acc[filter.label] = [];
                                    }
                                    acc[filter.label].push({
                                        readable_value: filter.readable_value,
                                        remove_url: filter.remove_url,
                                    });
                                }
                                return acc;
                            }, {}),
                    ).map(([label, values], index) => {
                        return (
                            <li className="active-filters__item" key={index}>
                                {remove_hidden ? (
                                    <>
                                        <h4 className="active-filter__heading">
                                            {label}:
                                        </h4>
                                        <p className="active-filter__text">
                                            {values
                                                .map((value) =>
                                                    value.readable_value
                                                        ? value.readable_value.replace(
                                                              /<\/?[^>]+(>|$)/g,
                                                              "",
                                                          )
                                                        : "",
                                                )
                                                .join(", ")}
                                        </p>
                                    </>
                                ) : (
                                    <a
                                        href={
                                            values.length === 1 &&
                                            values[0].remove_url
                                                ? `?${values[0].remove_url}`
                                                : "/barriers/search"
                                        }
                                        className="active-filters__item__link"
                                        title={`Remove ${label} filter`}
                                    >
                                        <h4 className="active-filter__heading">
                                            {label}:
                                        </h4>
                                        <p className="active-filter__text">
                                            {values
                                                .map((value) =>
                                                    value.readable_value
                                                        ? value.readable_value.replace(
                                                              /<\/?[^>]+(>|$)/g,
                                                              "",
                                                          )
                                                        : "",
                                                )
                                                .join(", ")}
                                        </p>
                                        <span className="sr-only govuk-visually-hidden">
                                            Activate link to remove {label}{" "}
                                            filter with value open quote{" "}
                                            {values
                                                .map((value) =>
                                                    value.readable_value
                                                        ? value.readable_value.replace(
                                                              /<\/?[^>]+(>|$)/g,
                                                              "",
                                                          )
                                                        : "",
                                                )
                                                .join(", ")}{" "}
                                            end quote.
                                        </span>
                                    </a>
                                )}
                            </li>
                        );
                    })}
                </ul>
            </div>
            <div className="govuk-grid-row">
                <h3 className="govuk-summary-card__title p-l-3">
                    Open barriers
                </h3>
                <SummaryCard
                    value={data && data.barriers.open}
                    description="barriers are open."
                    url="/search"
                    search_params={getSearchParamsFromForm()}
                />
                <SummaryCard
                    value={data && data.barriers.pb100}
                    description="PB100 barriers are open."
                    url="/search"
                    search_params={`${getSearchParamsFromForm()}&combined_priority=APPROVED`}
                />
                <SummaryCard
                    value={data && data.barriers.overseas_delivery}
                    description="Overseas delivery barriers are open."
                    url="/search"
                    search_params={getSearchParamsFromForm()}
                />
            </div>
            <div className="govuk-grid-row">
                <h3 className="govuk-summary-card__title p-l-3">
                    {`Barriers which have been resolved or are projected to be resolved between ${parseIso(
                        data && data.financial_year.current_start,
                    )} and ${parseIso(
                        data && data.financial_year.current_end,
                    )} current financial year`}
                    .
                </h3>
                <SummaryCard
                    value={data && data.barriers_current_year.open}
                    description="barriers have been resolved in the current financial year."
                    url="/search"
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
};

/**
 * Renders the summary cards component.
 * @param {string} elementId - The ID of the element to render the component in.
 * @returns {void}
 */
const renderSummaryCards = (elementId) => {
    const element = document.getElementById(elementId);

    const region = document.getElementById("region");
    const sector = document.getElementById("sector");
    const policy_team = document.getElementById("policy_team");
    const country = document.getElementById("country");

    const filterValues = {
        sector: getOptionValue(sector).options,
        policy_team: getOptionValue(policy_team).options,
        location: [
            ...getOptionValue(country).options,
            ...getOptionValue(region).options,
        ],
    };
    render(<SummaryCards filterValues={filterValues} />, element);
};

export default renderSummaryCards;
