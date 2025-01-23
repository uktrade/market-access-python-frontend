import React from "react";
import ReactDOM from "react-dom";
import { BARRIER_STATUS } from "../constants";
import { getCheckboxValues } from "../utils";
import { sharedData } from "./shared";


interface ApplyFilterButtonProps {
    text: string;
    filterValues: Record<string, any>;
}

interface updateBarrierInsightProps {
    (submitUrl: string): void;
}

interface HandleClickEvent extends React.MouseEvent<HTMLButtonElement> {
    preventDefault: () => void;
}

interface OptionValue {
    label: string;
    options: { value: string; label: string; checked: boolean }[];
}

const getOptionValue = (htmlElement: HTMLElement): OptionValue => {
    const label = htmlElement.querySelector("legend")!.textContent!.trim();
    const options = getCheckboxValues(htmlElement);
    return { label, options };
};

interface AdminAreasData {
    [key: string]: string[];
}

const formatAdminAreas = (searchParams: URLSearchParams): string[] => {
    const admin_areas: string[] = [];
    const adminAreasParam = searchParams.get("admin_areas");
    if (adminAreasParam) {
        const adminAreasData: AdminAreasData = JSON.parse(adminAreasParam);
        for (const key in adminAreasData) {
            const values: string[] = adminAreasData[key];
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

    const searchParams: URLSearchParams = new URLSearchParams(queryParams as string | string[][] | Record<string, string>);

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

const ApplyFilterButton: React.FC<ApplyFilterButtonProps> = (props: ApplyFilterButtonProps): JSX.Element => {

    const filterForm = document.querySelector<HTMLFormElement>("#filters-form");

    interface Option {
        value: string;
        label: string;
    }

    const handleGoogleAnalytics = (filters: { label: string; value: string; readable_value: string | string[]; }[]) => {
        let filtersForAnalytics = {
            region: [],
            policy_team: [],
            sector: [],
            location: [],
        };

        filters.forEach((filter: { label: string; value: string; readable_value: string | string[] }) => {
            if (filter.label == "sector" && filter.value) {
                filtersForAnalytics.sector.push(filter.readable_value as string);
            } else if (filter.label == "policy_team" && filter.value) {
                filtersForAnalytics.policy_team.push(filter.readable_value as string);
            } else if (filter.label == "location" && filter.value) {
                if (props.filterValues.region.some((e: Option) => e.value == filter.value)) {
                    filtersForAnalytics.region.push(filter.readable_value as string);
                } else {
                    filtersForAnalytics.location.push(filter.readable_value as string);
                }
            }
        });

        window["dataLayer"].push({
            event: "event",
            eventProps: filtersForAnalytics,
        });
    };

    const getReadableValue = (
        value: string,
        type: string,
    ): string | string[] => {
        if (type === "sector") {
            return props.filterValues.sector.find((sector: Option) => sector.value === value)
                .label;
        } else if (type === "policy_team") {
            return props.filterValues.policy_team.find(
                (policy_team: Option) =>
                    policy_team.value === value,
            ).label;
        } else if (type === "location") {
            // check if value is comma separated then split it and return an array
            if (value.includes(",")) {
                return value
                    .split(",")
                    .map(
                        (val) =>
                            props.filterValues.location.find(
                                (location: Option) =>
                                    location.value === val,
                            ).label,
                    );
            } else {
                return props.filterValues.location.find(
                    (location: Option) =>
                        location.value === value,
                ).label;
            }
        } else if (type === "status") {
            return BARRIER_STATUS[value];
        }
        return value;
    };

    const updateBarrierInsight: updateBarrierInsightProps = async (submitUrl: string): Promise<void> => {

        const response = await fetch(submitUrl, {
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "Content-Type": "application/json",
            },
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        // update  summary cards
        document.getElementById("open-count").innerHTML = data.barriers.open;
        document.getElementById("pb100-count").innerHTML = data.barriers.pb100;
        document.getElementById("overseas_delivery-count").innerHTML = data.barriers.overseas_delivery;
        document.getElementById("current_year-resolved-count").innerHTML = data.barriers_current_year.resolved;
        document.getElementById("current_year-pb100-count").innerHTML = data.barriers_current_year.pb100;
        document.getElementById("current_year-overseas_delivery-count").innerHTML = data.barriers_current_year.overseas_delivery;

        // Update chart using the exported ref
        sharedData.current = data;
    };

    const updateActiveFilters = () => {
        const searchParams = new URLSearchParams(window.location.search);
        const params: Record<string, string[]> = {};

        searchParams.forEach((value, key) => {
            if (!params[key]) {
                params[key] = [];
            }
            params[key].push(value);
        });

        const filters = Object.keys(params)
            .flatMap((key) => {
                const values = key === "sector" || key === "policy_team" ? params[key] : params[key][0].split(",");
                return values.map((val) => ({
                    label: key,
                    value: val,
                    readable_value: val && getReadableValue(val, key),
                    remove_url: new URLSearchParams(
                        addLocation(searchParams)
                    ).toString(),
                }));
            });
            handleGoogleAnalytics(filters);

        const activeFiltersContainer = document.getElementById("active-filters-container");
        if (activeFiltersContainer) {
            ReactDOM.render(
                <>
                    <h3 className="visually-hidden">Active filters:</h3>
                    <ul className="govuk-list">
                        {filters
                            .filter((v) => v.readable_value)
                            .map((filter, index) => (
                                <li className="active-filters__item" key={index}>
                                    {filter.remove_url ? (
                                        <a
                                            href={`?${filter.remove_url}`}
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
                                                Activate link to remove {filter.label} filter with value open quote {filter.readable_value} end quote.
                                            </span>
                                        </a>
                                    ) : (
                                        <>
                                            <h4 className="active-filter__heading">
                                                {filter.label}:
                                            </h4>
                                            <p className="active-filter__text">
                                                {filter.readable_value}
                                            </p>
                                        </>
                                    )}
                                </li>
                            ))}
                    </ul>
                </>,
                activeFiltersContainer
            );
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

        let queryString = new URLSearchParams(formData as any).toString();

        if (queryString === currentURLQuerystring) return;

        queryString = addLocation(queryString).toString();

        const formAction = filterForm.action.split("?")[0];
        const url = `${formAction}?${queryString}`;
        window.history.pushState({}, document.title, url);

        const submitURL = `/dashboard-summary/?${queryString}`;

        // update the dashboard
        updateBarrierInsight(submitURL);

        // update the active filters
        updateActiveFilters();
    };

    return (
        <>
            <button
                className={`govuk-button govuk-button--full-width`}
                type="button"
                onClick={handleClick}
                data-module="govuk-button"
            >
                {props.text}
            </button>
        </>
    );
};

export const renderApplyFilterButton = (elementId: string, buttonText: any) => {
    const element = document.getElementById(elementId);
    const text = buttonText || "Apply filters";
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
    ReactDOM.render(
        <ApplyFilterButton
            text={text}
            filterValues={filterValues}
        />,
        element,
    );
};
