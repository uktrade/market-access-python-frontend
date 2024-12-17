import React, { useEffect, useState, useCallback } from "react";
import { render } from "react-dom";

import { getCheckboxValues, parseIso } from "../utils";
import { BARRIER_STATUS } from "../constants";
import MultiSelectFilter from "../search/MultiSelectFilter";
import LocationFilter from "../search/LocationFilter";
import { handleBarChart } from "./charts";

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

const formatAdminAreas = (/** @type {URLSearchParams} */ searchParams) => {
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

const addLocation = (
    /** @type {string | URLSearchParams | string[][] | Record<string, string>} */ queryParams,
) => {
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

    let locationParams = [
        ...searchParams.getAll("country"), // Get all 'country' values
        searchParams.getAll("region"), // Get all 'region' values
        searchParams.get("country_trading_bloc"), // Get 'country_trading_bloc'
    ]
        .filter(Boolean)
        .join(","); // Filter out empty values and join with commas

    // Remove trailing comma
    if (locationParams.slice(-1) === ",") {
        locationParams = locationParams.slice(0, -1);
    }

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

/**
 * Renders the summary cards component & filters.
 *
 * @param {Object} props - The component props.
 * @param {Object} props.filterValues - The filter values.
 * @returns {JSX.Element} - The rendered component.
 */
const BarriersOverview = ({ filterValues }) => {
    const [form, setForm] = useState({
        region: "",
        sector: "",
        policy_team: "",
        location: "",
        country_trading_bloc: "",
    });

    const formRef = React.useRef(null);

    const [data, setData] = useState(null);

    const [filters, setFilters] = useState([]);

    const [chartData, setChartData] = useState({
        barChartData: {
            series: [
                {
                    name: "Value of barriers estimated to be resolved",
                    data: [],
                },
                {
                    name: "Value of resolved barriers",
                    data: [],
                },
            ],
            options: {
                chart: {
                    id: "basic-bar",
                    toolbar: {
                        show: true,
                    },
                },
                xaxis: {
                    categories: ["Loading ..."], // will be updated with label
                },
                yaxis: {
                    title: {
                        text: 'British pounds(£)',
                        style: {
                            color: '#3b5998',
                        },
                    },
                },
                title: {
                    text: "Total value of open barriers estimated to be resolved and resolved barriers( £-British pounds)",
                    align: "center",
                },
            },
            fill: {
                opacity: 1,
            },
        },
    });

    /**
     * Fetches data from the server based on the provided query parameters.
     *
     * @param {string} queryParams - The query parameters to be included in the request URL.
     * @returns {void}
     */
    const fetchData = (queryParams) => {
        // update the current URL with the new query params
        const searchParams = new URLSearchParams(queryParams);

        // remove any empty values
        for (const [key, value] of searchParams.entries()) {
            if (value === "" || value === null || value === undefined) {
                searchParams.delete(key);
            }
        }

        const searchParamsWithLocation = addLocation(searchParams);

        window.history.pushState(
            {},
            "",
            `?${searchParamsWithLocation.toString()}`,
        );

        const url = searchParamsWithLocation
            ? `/dashboard-summary/?${searchParamsWithLocation.toString()}`
            : "/dashboard-summary/";

        fetch(url, {
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "Content-Type": "application/json",
            },
        }).then((response) => {
            response.json().then((data) => {
                setData(data);
                setChartData((prevState) => ({
                    ...prevState,
                    barChartData: {
                        ...prevState.barChartData,
                        series: [
                            {
                                name: "Value of barriers estimated to be resolved",
                                data:
                                    data &&
                                        data.barrier_value_chart
                                            .estimated_barriers_value
                                        ? [
                                            data.barrier_value_chart
                                                .estimated_barriers_value,
                                        ]
                                        : [],
                            },
                            {
                                name: "Value of resolved barriers",
                                data:
                                    data &&
                                        data.barrier_value_chart
                                            .resolved_barriers_value
                                        ? [
                                            data.barrier_value_chart
                                                .resolved_barriers_value,
                                        ]
                                        : [],
                            },
                        ],
                        options: {
                            ...prevState.barChartData.options,
                            xaxis: {
                                categories: [
                                    ` ${parseIso(
                                        data?.financial_year?.current_start,
                                    )} to ${parseIso(
                                        data?.financial_year?.current_end,
                                    )}`,
                                ],
                            },
                            yaxis: {
                                title: {
                                    text: 'British pounds(£)',
                                    style: {
                                        color: '#3b5998',
                                    },
                                },

                            },
                        },
                    },
                }));
            });
        });
    };

    const getSearchParamsFromForm = () => {
        if (!formRef.current) {
            return "";
        }
        const formData = new FormData(formRef.current);
        // @ts-ignore
        return new URLSearchParams(formData).toString();
    };

    const getFinancialYearSearchParams = (field) => {
        if (!formRef.current) {
            return "";
        }
        const formData = new FormData(formRef.current);
        // @ts-ignore
        const searchParams = new URLSearchParams(formData);
        // Append the year and month filters for the financial year
        const start_date = new Date(data?.financial_year?.current_start);
        const end_date = new Date(data?.financial_year?.current_end);

        if (field == "status") {
            //Resolved in full from this date
            searchParams.append(
                "status_date_resolved_in_full_0_0",
                (start_date.getMonth() + 1).toString(),
            );
            searchParams.append(
                "status_date_resolved_in_full_0_1",
                start_date.getFullYear().toString(),
            );
            //to this date
            searchParams.append(
                "status_date_resolved_in_full_1_0",
                (end_date.getMonth() + 1).toString(),
            );
            searchParams.append(
                "status_date_resolved_in_full_1_1",
                end_date.getFullYear().toString(),
            );
        }
        if (field == "estimated_resolution_date") {
            //Estimated resolution date from this date
            searchParams.append(
                "estimated_resolution_date_resolved_in_part_0_0",
                (start_date.getMonth() + 1).toString(),
            );
            searchParams.append(
                "estimated_resolution_date_resolved_in_part_0_1",
                start_date.getFullYear().toString(),
            );
            //to this date
            searchParams.append(
                "estimated_resolution_date_resolved_in_part_1_0",
                (end_date.getMonth() + 1).toString(),
            );
            searchParams.append(
                "estimated_resolution_date_resolved_in_part_1_1",
                end_date.getFullYear().toString(),
            );
            //Estimated resolution date from this date
            searchParams.append(
                "status_date_open_in_progress_0_0",
                (start_date.getMonth() + 1).toString(),
            );
            searchParams.append(
                "status_date_open_in_progress_0_1",
                start_date.getFullYear().toString(),
            );
            //to this date
            searchParams.append(
                "status_date_open_in_progress_1_0",
                (end_date.getMonth() + 1).toString(),
            );
            searchParams.append(
                "status_date_open_in_progress_1_1",
                end_date.getFullYear().toString(),
            );
        }

        return searchParams.toString();
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
                (/** @type {{ value: string; }} */ policy_team) =>
                    policy_team.value === value,
            ).label;
        } else if (type === "location") {
            // check if value is comma separated then split it and return an array
            if (value.includes(",")) {
                return value
                    .split(",")
                    .map(
                        (val) =>
                            filterValues.location.find(
                                (/** @type {{ value: string; }} */ location) =>
                                    location.value === val,
                            ).label,
                    );
            } else {
                return filterValues.location.find(
                    (/** @type {{ value: string; }} */ location) =>
                        location.value === value,
                ).label;
            }
        } else if (type === "status") {
            return BARRIER_STATUS[value];
        }
        return value;
    };

    const updateFilters = useCallback(() => {
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
                let values = [];
                if (key == "sector" || key == "policy_team") {
                    values = params[key];
                } else {
                    values = params[key][0].split(",");
                }
                return values.map((/** @type {string} */ val) => ({
                    label: key,
                    value: val,
                    readable_value: val && getReadableValue(val, key),
                }));
            })
            .flat();
        setFilters(filters);
        handleGoogleAnalytics(filters);
    }, [window.location.search]);

    const handleGoogleAnalytics = (filters) => {
        let filtersForAnalytics = {
            region: [],
            policy_team: [],
            sector: [],
            location: [],
        };

        filters.forEach((filter) => {
            if (filter.label == "sector" && filter.value) {
                filtersForAnalytics.sector.push(filter.readable_value);
            } else if (filter.label == "policy_team" && filter.value) {
                filtersForAnalytics.policy_team.push(filter.readable_value);
            } else if (filter.label == "location" && filter.value) {
                if (filterValues.region.some((e) => e.value == filter.value)) {
                    filtersForAnalytics.region.push(filter.readable_value);
                } else {
                    filtersForAnalytics.location.push(filter.readable_value);
                }
            }
        });

        window["dataLayer"].push({
            event: "event",
            eventProps: filtersForAnalytics,
        });
    };

    const handleInputChange = ({ name, value }) => {
        // set the new value with the name of the input to the query string in the url
        setForm((prevState) => {
            const newForm = { ...prevState, [name]: value };
            // update the current URL with the new query params
            const searchParams = new URLSearchParams();
            for (const [key, value] of Object.entries(newForm)) {
                if (["", null].indexOf(value) === -1) {
                    if (key === "location") {
                        // @ts-ignore
                        const selectedIds = newForm[key].selectedLocationIds;
                        if (selectedIds.length > 0) {
                            searchParams.append(key, selectedIds.join(","));
                        }
                    } else {
                        searchParams.append(key, value);
                    }
                }
            }
            // update the current URL with the new query params
            const searchParamsWithLocation = addLocation(searchParams);
            window.history.replaceState(
                {},
                "",
                `?${searchParamsWithLocation.toString()}`,
            );
            return newForm;
        });
    };

    const handleSubmit = (/** @type {any} */ event) => {
        event.preventDefault();
        const params = getSearchParamsFromForm();
        // @ts-ignore
        fetchData(params);
        // update the filters
        updateFilters();
    };

    useEffect(() => {
        fetchData("");
    }, []);

    return (
        <>
            <div className="govuk-grid-row">
                <div className="govuk-grid-column-one-quarter">
                    <fieldset className="govuk-fieldset">
                        <legend className="govuk-fieldset__legend govuk-fieldset__legend--l">
                            <h3 className="govuk-fieldset__heading govuk-summary-card__title">
                                Filters
                            </h3>
                        </legend>
                        <form
                            id="filters-form"
                            onSubmit={handleSubmit}
                            ref={formRef}
                        >
                            <MultiSelectFilter
                                label="Region"
                                options={filterValues.region}
                                inputId="region"
                                placeholder="Search regions"
                                onChange={handleInputChange}
                            />
                            <MultiSelectFilter
                                label="Sector"
                                options={filterValues.sector}
                                inputId="sector"
                                placeholder="Search sectors"
                                onChange={handleInputChange}
                            />
                            <LocationFilter
                                label="Location"
                                countries={filterValues.location}
                                tradingBlocs={filterValues.tradingBlocs}
                                tradingBlocData={filterValues.tradingBlocsData}
                                adminAreaData={filterValues.adminAreas}
                                adminAreasCountries={
                                    filterValues.adminAreasCountries
                                }
                                onChange={handleInputChange}
                            />
                            <MultiSelectFilter
                                label="Policy team"
                                options={filterValues.policy_team}
                                inputId="policy_team"
                                placeholder="Search policy teams"
                                onChange={handleInputChange}
                            />
                            <button
                                type="submit"
                                className="govuk-button govuk-button--full-width"
                                id="apply-filters-button"
                                disabled={Object.values(form).every(
                                    (value) => value === "",
                                )}
                            >
                                Apply filters
                            </button>
                        </form>
                    </fieldset>
                </div>
                <div className="govuk-grid-column-three-quarters">
                    <h2 className="govuk-summary-card__title">
                        Barrier insights
                        <span className="govuk-caption-m">Current filters:</span>
                    </h2>

                    <div className="p-l-3" id="active filters">

                        <ul className="govuk-list">
                            {filters
                                .filter((v) => v.readable_value)
                                .map((filter, index) => (
                                    <li
                                        className="active-filters__item"
                                        key={index}
                                    >
                                        <h4 className="active-filter__heading">
                                            {filter.label === "policy_team"
                                                ? "policy team"
                                                : filter.label}
                                            {": "}
                                        </h4>
                                        <p className="active-filter__text">
                                            {filter.readable_value}
                                        </p>
                                    </li>
                                ))}
                        </ul>
                    </div>
                    <div className="govuk-grid-row">
                        <h3 className="govuk-summary-card__title p-l-3">
                            Open barriers
                        </h3>
                        <span className="govuk-caption-m p-l-3">
                            This includes all open and resolved in part
                            barriers.
                        </span>
                        <SummaryCard
                            value={data?.barriers?.open}
                            description="barriers are open in total."
                            url="/search"
                            search_params={`${getSearchParamsFromForm()}&status=2&status=3`}
                        />
                        <SummaryCard
                            value={data?.barriers?.pb100}
                            description="PB100 barriers are open."
                            url="/search"
                            search_params={`${getSearchParamsFromForm()}&status=2&status=3&combined_priority=APPROVED`}
                        />
                        <SummaryCard
                            value={data?.barriers?.overseas_delivery}
                            description="Overseas delivery barriers are open."
                            url="/search"
                            search_params={`${getSearchParamsFromForm()}&status=2&status=3&combined_priority=OVERSEAS`}
                        />
                    </div>
                    <div className="govuk-grid-row">
                        <h3 className="govuk-summary-card__title p-l-3">
                            {`Resolved barriers for financial year: ${data
                                ? parseIso(
                                    data?.financial_year?.current_start,
                                )
                                : null
                                } to ${data
                                    ? parseIso(
                                        data?.financial_year?.current_end,
                                    )
                                    : null
                                }`}
                        </h3>
                        <span className="govuk-caption-m p-l-3">
                            This includes resolved barriers and those with an
                            estimated resolution date in the financial year
                        </span>

                        <SummaryCard
                            value={data?.barriers_current_year?.resolved}
                            description="barriers have been resolved in full in the financial year."
                            url="/search"
                            search_params={`${getSearchParamsFromForm()}${getFinancialYearSearchParams(
                                "status",
                            )}&status=4`}
                        />
                        <SummaryCard
                            value={data?.barriers_current_year?.pb100}
                            description="PB100 barriers have an estimated resolution date in the financial year."
                            url="/search"
                            search_params={`${getSearchParamsFromForm()}${getFinancialYearSearchParams(
                                "estimated_resolution_date",
                            )}&status=2&status=3&combined_priority=APPROVED`}
                        />
                        <SummaryCard
                            value={
                                data?.barriers_current_year?.overseas_delivery
                            }
                            description="Overseas delivery barriers have an estimated resolution date in the financial year."
                            url="/search"
                            search_params={`${getSearchParamsFromForm()}${getFinancialYearSearchParams(
                                "estimated_resolution_date",
                            )}&status=2&status=3&combined_priority=OVERSEAS`}
                        />
                    </div>
                </div>
            </div>
            <div className="govuk-grid-row">
                <div className="govuk-grid-column-full">
                    {chartData.barChartData.series[0].data.length > 0 ||
                        chartData.barChartData.series[1].data.length > 0 ? (
                        handleBarChart(chartData.barChartData)
                    ) : (
                        <div className="dashboard-chart">
                            <h3 className="govuk-heading-s">
                                Total value of barriers resolved and estimated
                            </h3>
                            <p className="govuk-inset-text">
                                Unable to display chart. No data available for
                                current filters
                            </p>
                            {chartData.barChartData.series[0].data.length ===
                                0 && (
                                    <p className="govuk-body-s">
                                        No resolved barriers found in the date range
                                    </p>
                                )}
                            {chartData.barChartData.series[0].data.length ===
                                1 && (
                                    <p className="govuk-body-s">
                                        No barriers with an estimated resolution in
                                        the date range{" "}
                                    </p>
                                )}
                        </div>
                    )}
                </div>
            </div>
        </>
    );
};

/**
 * Renders the summary cards component.
 * @param {string} elementId - The ID of the element to render the component in.
 * @returns {void}
 */
const renderBarriersOverview = (elementId) => {
    const element = document.getElementById(elementId);

    const region = document.getElementById("region");
    const sector = document.getElementById("sector");
    const policy_team = document.getElementById("policy_team");
    const country = document.getElementById("country");
    const tradingBlocs = document.getElementById("country_trading_bloc");
    const tradingBlocsData = JSON.parse(
        document.getElementById("trading-blocs-data").textContent,
    );
    const adminAreas = JSON.parse(
        document.getElementById("admin-areas-data").textContent,
    );
    const adminAreasCountries = JSON.parse(
        document.getElementById("countries-with-admin-areas-data").textContent,
    );

    const filterValues = {
        region: getOptionValue(region).options,
        sector: getOptionValue(sector).options,
        policy_team: getOptionValue(policy_team).options,
        location: [
            ...getOptionValue(country).options,
            ...getOptionValue(region).options,
            ...getOptionValue(tradingBlocs).options,
        ],
        tradingBlocs: getOptionValue(tradingBlocs).options,
        tradingBlocsData,
        adminAreas,
        adminAreasCountries,
    };
    render(<BarriersOverview filterValues={filterValues} />, element);
};

export default renderBarriersOverview;
