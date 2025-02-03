import React from "react";
import ReactDOM from "react-dom";
import { BARRIER_STATUS } from "../constants";
import { getCheckboxValues } from "../utils";
import { useWindowQueryParams } from "../hooks";


interface ApplyFilterControllerProps {
    text: string;
    filterValues: Record<string, any>;
}

interface updateBarrierInsightProps {
    (submitUrl: string): void;
}

interface HandleClickEvent extends React.MouseEvent<HTMLButtonElement> {
    preventDefault: () => void;
}

interface Option {
    value: string;
    label: string;
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

const _makeHumanReadable = (value: string): string => {
    return value.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')
}

const addLocation = (queryParams: string | URLSearchParams | string[][] | Record<string, string>) => {
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

const ApplyFilterController: React.FC<ApplyFilterControllerProps> = (props: ApplyFilterControllerProps): JSX.Element => {

    const queryParams = useWindowQueryParams();

    const filterForm = document.querySelector<HTMLFormElement>("#filters-form");

    const getSearchParamsFromForm = () => {
        if (!filterForm) {
            return "";
        }
        const formData = new FormData(filterForm);
        const formDataObject: Record<string, string> = {};
        formData.forEach((value, key) => {
            formDataObject[key] = value.toString();
        });
        return new URLSearchParams(formDataObject).toString();
    };

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
        } else if (["location", "region", "country"].includes(type)) {
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
        } else if (type === "country_trading_bloc") {
            return props.filterValues.tradingBlocs.find(
                (tradingBloc: Option) => tradingBloc.value === value,
            ).label;
        }
        return value;
    };

    // const getReadableValue = (
    //     value: string,
    //     type: string,
    // ) => {
    //     if (type === "sector") {
    //         return props.filterValues.sector.find((sector) => sector.value === value)
    //             .label;
    //     } else if (type === "policy_team") {
    //         return props.filterValues.policy_team.find(
    //             (/** @type {{ value: string; }} */ policy_team) =>
    //                 policy_team.value === value,
    //         ).label;
    //     } else if (type === "location") {
    //         // check if value is comma separated then split it and return an array
    //         if (value.includes(",")) {
    //             return value
    //                 .split(",")
    //                 .map(
    //                     (val) =>
    //                         props.filterValues.location.find(
    //                             (/** @type {{ value: string; }} */ location) =>
    //                                 location.value === val,
    //                         ).label,
    //                 );
    //         } else {
    //             return props.filterValues.location.find(
    //                 (/** @type {{ value: string; }} */ location) =>
    //                     location.value === value,
    //             ).label;
    //         }
    //     } else if (type === "status") {
    //         return BARRIER_STATUS[value];
    //     }
    //     return value;
    // };

    const getFinancialYearSearchParam = (field: string, financial_year: any) => {
        const searchParams = new URLSearchParams(getSearchParamsFromForm());
        const start_date = new Date(financial_year.current_start);
        const end_date = new Date(financial_year.current_end);

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
    }

    const updateBarrierInsight: updateBarrierInsightProps = async (submitUrl: string): Promise<void> => {
        // Constants for element IDs
        const elementIds = {
            current: ["open-count", "pb100-count", "overseas_delivery-count"],
            yearly: ["resolved", "pb100", "overseas_delivery"].map(id => `current_year-${id}-count`)
        };

        // Set loading state for all elements
        [...elementIds.current, ...elementIds.yearly].forEach(id => {
            document.getElementById(id).innerHTML = "Loading...";
        });

        const elementLinkUrls = {
            current: ["open-link", "pb100-link", "overseas_delivery-link"],
            yearly: ["resolved", "pb100", "overseas_delivery"].map(id => `current_year-${id}-link`)
        };

        // Fetch data
        const response = await fetch(submitUrl, {
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "Content-Type": "application/json",
            },
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const { barriers, barriers_current_year, financial_year } = await response.json();

        // Update current barriers
        elementIds.current.forEach((id, index) => {
            const keys = ["open", "pb100", "overseas_delivery"];
            document.getElementById(id).innerHTML = barriers[keys[index]];
        });

        // Update yearly barriers
        elementIds.yearly.forEach((id, index) => {
            const keys = ["resolved", "pb100", "overseas_delivery"];
            document.getElementById(id).innerHTML = barriers_current_year[keys[index]];
        });

        // Update financial year url
        const status = getFinancialYearSearchParam("status", financial_year);
        const estimated_resolution_date = getFinancialYearSearchParam("estimated_resolution_date", financial_year);

        const queryParams = getSearchParamsFromForm();

        const linkDict = {
            "open-link": `/search/?${queryParams}&status=2&status=3`, // Open link
            "pb100-link": `/search/?${queryParams}&status=2&status=3&combined_priority=APPROVED`, // PB100 link
            "overseas_delivery-link": `/search/?${queryParams}&status=2&status=3&combined_priority=OVERSEAS`, // Overseas delivery link
            "current_year-resolved-link": `/search/?${status}&status=4`, // Resolved link
            "current_year-pb100-link": `/search/?${estimated_resolution_date}&status=2&status=3&combined_priority=APPROVED`, // PB100 link current year
            "current_year-overseas_delivery-link": `/search/?${estimated_resolution_date}&status=2&status=3&combined_priority=OVERSEAS` // Overseas delivery link current year
        }

        // update the divs with the new links
        Object.keys(linkDict).forEach((key) => {
            const element = document.getElementById(key);
            if (element) {
                element.querySelector('a').href = linkDict[key];
            }
        });
    };

    const updateActiveFilters = () => {

        // Get initial search params
        const initialSearchParams = new URLSearchParams(window.location.search);

        // Combine multiple values of the same parameter
        const paramMap = new Map<string, string[]>();
        initialSearchParams.forEach((value, key) => {
            if (!paramMap.has(key)) {
            paramMap.set(key, []);
            }
            paramMap.get(key)!.push(value);
        });

        // Create new URLSearchParams with combined values
        const searchParams = new URLSearchParams();
        paramMap.forEach((values, key) => {
            searchParams.append(key, values.join(','));
        });

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
                    label: _makeHumanReadable(key),
                    value: val,
                    readable_value: val && getReadableValue(val, key),
                    remove_url: new URLSearchParams(
                        addLocation(searchParams)
                    ).toString(),
                }));
            });
            handleGoogleAnalytics(filters);

        const activeFiltersContainer = document.getElementById("active filters");
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

    const handleClick = async (event: HandleClickEvent, additionalQueryParams: string | null = null) => {
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

        // Remove empty query parameters
        queryString = queryString.split('&')
            .filter(param => {
            const [_key, value] = param.split('=');
            return value !== '' && value !== undefined;
            })
            .join('&');

        const formAction = filterForm.action.split("?")[0];
        let url = `${formAction}?${queryString}`;
        if (additionalQueryParams) {
            url += `&${additionalQueryParams}`;
        }
        window.history.pushState({}, document.title, url);
    };

    React.useEffect(() => {
        const queryString = new URLSearchParams(window.location.search).toString();
        const submitURL = `/dashboard-summary/?${queryString}`;

        // update the dashboard
        updateBarrierInsight(submitURL);

        // update the active filters
        updateActiveFilters();
    }, [queryParams]);

    React.useEffect(() => {
        const formFieldsContainer = document.querySelector("#filter-form-fields");

        if (!formFieldsContainer) return;

        const observer = new MutationObserver((mutations) => {
            for (const mutation of mutations) {
                if (mutation.type !== "childList" ||
                    mutation.oldValue === mutation.target.textContent ||
                    !(mutation.target instanceof HTMLDivElement)) {
                    continue;
                }

                const input = mutation.target.querySelector("input");
                if (!input) continue;

                handleClick(
                    { preventDefault: () => {} } as HandleClickEvent);
            }
        });

        if (formFieldsContainer) {
            observer.observe(formFieldsContainer, {
                characterData: false,
                childList: true,
                subtree: true,
                attributes: false,
                characterDataOldValue: false,
            });
        }

        const handleCheckboxChange = ({ target }: Event) => {
            if (!(target instanceof HTMLInputElement) || target.type !== "checkbox") return;

            const { name, checked, value } = target;
            if (!name) return;

            const searchParams = new URLSearchParams(window.location.search);
            const values = new Set(searchParams.getAll(name));

            if (checked && !values.has(value)) {
                values.add(value);
            } else {
                values.delete(value);
            }

            const queryString = Array.from(values).length > 0
                ? Array.from(values).map(v => `${name}=${v}`).join('&')
                : '';

            handleClick(
                { preventDefault: () => {} } as HandleClickEvent,
                queryString
            );
        };

        // Attach listener
        formFieldsContainer.addEventListener("change", handleCheckboxChange);

        // Clean up
        return () => {
            formFieldsContainer.removeEventListener("change", handleCheckboxChange);
            observer.disconnect();
        };

    }, []); // Empty dependency array since we only want this to run once on mount

    return null; // Controller component doesn't need to render anything
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
        ],
        tradingBlocs: getOptionValue(tradingBlocs).options,
        tradingBlocsData,
        adminAreas,
        adminAreasCountries,
    };
    ReactDOM.render(
        <ApplyFilterController
            text={text}
            filterValues={filterValues}
        />,
        element,
    );
};
