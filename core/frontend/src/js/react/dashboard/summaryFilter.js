import React, { useEffect, useState } from "react";
import { render } from "react-dom";

import { getCheckboxValues } from "../utils";
import { BARRIER_STATUS } from "../constants";
import MultiSelectFilter from "../search/MultiSelectFilter";
import LocationFilter from "../search/LocationFilter";
import {
    handleBarChart,
    handlePieChart,
    handleStackedBarChart,
} from "./charts";

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
    const [form, setForm] = useState({
        region: "",
        sector: "",
        policy_team: "",
        location: "",
        country_trading_bloc: "",
    });

    const formRef = React.useRef(null);

    const [data, setData] = useState(null);

    const currentMonth = new Date().toLocaleString("default", {
        month: "long",
    });

    const [chartData, setChartData] = useState({
        pieChatData: {
            series: data ? data.barrier_status_chart?.series : [],
            options: {
                chart: {
                    id: "basic-pie",
                },
                title: {
                    text: "Total value of open and partially resolved barrier by priority type",
                    align: "center",
                },
                dataLabels: {
                    enabled: false,
                },
                labels: data ? data.barrier_status_chart?.labels : [],
                colors: ["#28a197", "#003078", "#d4351c", "#912b88"],
            },
        },
        barChartData: {
            series: [
                {
                    name: "Open barriers",
                    data: data
                        ? data.total_value_chart?.open_barriers_value
                        : [],
                },
                {
                    name: "Resolved barriers",
                    data: data
                        ? data.total_value_chart?.resolved_barriers_value
                        : [],
                },
            ],
            options: {
                chart: {
                    id: "basic-bar",
                },
                plotOptions: {
                    bar: {
                        horizontal: false,
                        columnWidth: "100%",
                    },
                },
                fill: {
                    opacity: 1,
                },
                stroke: {
                    width: 5,
                    colors: ["transparent"],
                },
                dataLabels: {
                    enabled: true,
                },
                xaxis: {
                    categories: data ? data.total_value_chart?.labels : [],
                },
            },
        },
        stackedBarChartData: {
            series: [
                {
                    name: "Value of resolved barriers",
                    data: data
                        ? data.barrier_value_chart?.resolved_barriers_value
                        : [],
                },
                {
                    name: "Value of barriers estimated to be resolved",
                    data: data
                        ? data.barrier_value_chart?.estimated_barriers_value
                        : [],
                },
            ],
            options: {
                chart: {
                    id: "stacked-bar",
                },
                xaxis: {
                    categories: [currentMonth],
                },
                yaxis: {
                    title: {
                        text: "£",
                    },
                },
                title: {
                    text: "Total value of barriers resolved and estimated in the current financial year",
                    align: "center",
                },
                fill: {
                    opacity: 1,
                },
                colors: ["#912b88", "#003078"],
            },
        },
    });

    const [filters, setFilters] = useState([]);

    /**
     * Fetches data from the server based on the provided query parameters.
     *
     * @param {string} queryParams - The query parameters to be included in the request URL.
     * @returns {void}
     */
    const fetchData = (queryParams) => {
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
        fetch(url, {
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "Content-Type": "application/json",
            },
        }).then((response) => {
            response.json().then((data) => {
                setData(data);
                // set the data for the charts
                setChartData((prevState) => ({
                    ...prevState,
                    pieChatData: {
                        ...prevState.pieChatData,
                        series: data.barrier_status_chart?.series,
                        options: {
                            ...prevState.pieChatData.options,
                            labels: data.barrier_status_chart?.labels,
                        },
                    },
                    barChartData: {
                        ...prevState.barChartData,
                        series: [
                            {
                                name: "Open barriers",
                                data: data.total_value_chart
                                    .open_barriers_value,
                            },
                            {
                                name: "Resolved barriers",
                                data: data.total_value_chart
                                    .resolved_barriers_value,
                            },
                        ],
                        options: {
                            ...prevState.barChartData.options,
                            xaxis: {
                                categories: data.total_value_chart.labels,
                            },
                        },
                    },
                    stackedBarChartData: {
                        ...prevState.stackedBarChartData,
                        series: [
                            {
                                name: "Value of resolved barriers",
                                data: data.barrier_value_chart
                                    .resolved_barriers_value,
                            },
                            {
                                name: "Value of barriers estimated to be resolved",
                                data: data.barrier_value_chart
                                    .estimated_barriers_value,
                            },
                        ],
                    },
                }));
            });
        });
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
        if (!formRef.current) {
            return "";
        }
        const formData = new FormData(formRef.current);
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

    const handleInputChange = ({ name, value }) => {
        // set the new value with the name of the input to the query string in the url
        setForm((prevState) => {
            const newForm = { ...prevState, [name]: value };
            // update the current URL with the new query params
            const searchParams = new URLSearchParams();
            for (const [key, value] of Object.entries(newForm)) {
                if (["", null].indexOf(value) === -1) {
                    searchParams.append(key, value);
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
    };

    const removeFilter = (/** @type {any} */ filter) => {
        // remove from filter list and update the URL
        setFilters((prevFilters) =>
            prevFilters.filter((f) => f.label !== filter.label),
        );
        // remove the filter from the URL
        const searchParams = new URLSearchParams(window.location.search);
        searchParams.delete(filter.label);
        window.history.pushState({}, "", `?${searchParams.toString()}`);
    };

    useEffect(() => {
        fetchData("");
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
        <div>
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
                            {filters.length > 0 && (
                                <a
                                    id="clear-filters-button"
                                    className="filter-items__clear"
                                    href="{% url 'barriers:home' %}"
                                >
                                    Remove all filters
                                </a>
                            )}
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
                    <h3 className="govuk-summary-card__title">Summary data</h3>
                    <div className="p-l-3" id="active-filters">
                        <ul className="govuk-list">
                            {filters
                                .filter((v) => v.readable_value)
                                .map((filter, index) => (
                                    <li
                                        className="active-filters__item"
                                        key={index}
                                    >
                                        <span
                                            onClick={(e) => {
                                                e.preventDefault();
                                                removeFilter(filter);
                                            }}
                                            className="active-filters__item__link"
                                            title={`Remove ${filter.label} filter`}
                                        >
                                            <h4 className="active-filter__heading">
                                                {filter.label}:
                                            </h4>
                                            <p className="active-filter__text">
                                                {filter.readable_value}
                                            </p>
                                            <span className="sr-only govuk-visually-hidden">
                                                Activate link to remove{" "}
                                                {filter.label} filter with value{" "}
                                                {filter.readable_value}.
                                            </span>
                                        </span>
                                    </li>
                                ))}
                        </ul>
                    </div>
                    <div className="govuk-grid-row">
                        <h3 className="govuk-summary-card__title p-l-3">
                            Open barriers
                        </h3>
                        <SummaryCard
                            value={data?.barriers?.open}
                            description="barriers are open."
                            url="/search"
                            search_params={getSearchParamsFromForm()}
                        />
                        <SummaryCard
                            value={data?.barriers?.pb100}
                            description="PB100 barriers are open."
                            url="/search"
                            search_params={`${getSearchParamsFromForm()}&combined_priority=APPROVED`}
                        />
                        <SummaryCard
                            value={data?.barriers?.overseas_delivery}
                            description="Overseas delivery barriers are open."
                            url="/search"
                            search_params={getSearchParamsFromForm()}
                        />
                    </div>
                    <div className="govuk-grid-row">
                        <h3 className="govuk-summary-card__title p-l-3">
                            {`Barriers which have been resolved or are projected to be resolved between ${parseIso(
                                data?.financial_year?.current_start,
                            )} and ${parseIso(
                                data?.financial_year?.current_end,
                            )} current financial year`}
                        </h3>
                        <SummaryCard
                            value={data?.barriers_current_year?.open}
                            description="barriers have been resolved in the current financial year."
                            url="/search"
                            search_params={getSearchParamsFromForm()}
                        />
                        <SummaryCard
                            value={data?.barriers_current_year?.pb100}
                            description="PB100 barriers are estimated to be resolved in the current financial year."
                            url="#"
                            search_params=""
                        />
                        <SummaryCard
                            value={
                                data?.barriers_current_year?.overseas_delivery
                            }
                            description="Overseas delivery barriers are estimated to be resolved in the current financial year."
                            url="#"
                            search_params=""
                        />
                    </div>
                </div>
            </div>
            <div className="govuk-grid-row">
                <div className="govuk-grid-row">
                    <div className="govuk-grid-column-full">
                        {data?.barrier_value_chart.resolved_barriers_value &&
                        data?.barrier_value_chart.estimated_barriers_value ? (
                            handleStackedBarChart(chartData.stackedBarChartData)
                        ) : (
                            <div className="dashboard-chart">
                                <h3 className="govuk-heading-s">
                                    Total value of barriers resolved and
                                    estimated in the current finanacial year
                                </h3>
                                <p className="govuk-inset-text">
                                    Unable to display chart. No data available
                                    for current filters
                                </p>
                                {!data?.barrier_value_chart
                                    .resolved_barriers_value && (
                                    <p className="govuk-body-s">
                                        No resolved barriers found
                                    </p>
                                )}
                                {!data?.barrier_value_chart
                                    .estimated_barriers_value && (
                                    <p className="govuk-body-s">
                                        No barriers with an estimated resolution
                                        in the current year found{" "}
                                    </p>
                                )}
                            </div>
                        )}
                    </div>
                </div>
                <div className="govuk-grid-row">
                    <div className="govuk-grid-column-one-half">
                        {data?.total_value_chart.open_barriers_value &&
                        data?.total_value_chart.resolved_barriers_value ? (
                            handleBarChart(chartData.barChartData)
                        ) : (
                            <div className="dashboard-chart">
                                <h3 className="govuk-heading-s">
                                    Total barrier value
                                </h3>
                                <p className="govuk-inset-text">
                                    Unable to display chart. No data available
                                    for current filters
                                </p>
                                {!data?.total_value_chart
                                    .open_barriers_value && (
                                    <p className="govuk-body-s">
                                        No open barriers found
                                    </p>
                                )}
                                {!data?.total_value_chart
                                    .resolved_barriers_value && (
                                    <p className="govuk-body-s">
                                        No resolved barriers found
                                    </p>
                                )}
                            </div>
                        )}
                    </div>
                    <div className="govuk-grid-column-one-half">
                        {data?.barriers_by_status_chart.series ? (
                            handlePieChart(chartData.pieChatData)
                        ) : (
                            <div className="dashboard-chart">
                                <h3 className="govuk-heading-s">
                                    Total value of open and partially resolved
                                    barrier by status
                                </h3>
                                <p className="govuk-inset-text">
                                    Unable to display chart. No data available
                                    for current filters
                                </p>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
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
    render(<SummaryCards filterValues={filterValues} />, element);
};

export default renderSummaryCards;
