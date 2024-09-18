import React, { useState } from "react";

import TypeAhead from "../forms/TypeAhead";

function TradingBlocFilter(props) {
    const selectedTradingBlocs = props.tradingBlocs.reduce(
        (selected, tradingBloc) => {
            if (props.selectedTradingBlocIds.includes(tradingBloc.value))
                selected.push(tradingBloc);
            return selected;
        },
        [],
    );

    return (
        <div className="checkbox-filter govuk-!-width-full">
            {selectedTradingBlocs.map((tradingBloc, index) => (
                <div className="checkbox-filter__item" key={tradingBloc.value}>
                    <input
                        className="checkbox-filter__input"
                        id={"country_trading_bloc-" + index}
                        name="country_trading_bloc"
                        type="checkbox"
                        value={tradingBloc.value}
                        defaultChecked={tradingBloc.checked}
                    />
                    <label
                        className="govuk-label checkbox-filter__label"
                        htmlFor={"country_trading_bloc-" + index}
                    >
                        {tradingBloc.label}
                    </label>
                </div>
            ))}
        </div>
    );
}

function AdminAreaFilter(props) {
    const adminAreas = props.adminAreas;
    const selectedCountriesWithAdminAreas = props.selectedAdminAreaCountryIds;
    const countriesList = props.countryNames;

    const getCountryName = (adminAreasCountry) => {
        for (let i = 0; i < countriesList.length; i++) {
            if (countriesList[i]["id"] == adminAreasCountry) {
                return countriesList[i]["name"];
            }
        }
    };

    const getDefaultValue = (adminAreasList, adminAreasCountry) => {
        const defaultValues = [];
        for (let i = 0; i < adminAreasList.length; i++) {
            if (
                props.selectedAdminAreaIds[adminAreasCountry].includes(
                    adminAreasList[i]["value"],
                )
            ) {
                defaultValues.push(adminAreasList[i]);
            }
        }
        return defaultValues;
    };

    return (
        <div id="admin_areas_container" className="govuk-!-padding-top-2">
            <input
                type="hidden"
                id="admin_areas"
                name="admin_areas"
                value={JSON.stringify(props.selectedAdminAreaIds)}
            />
            {selectedCountriesWithAdminAreas.map((adminAreasCountry, index) => (
                <div
                    id={"admin_areas_" + adminAreasCountry}
                    key={adminAreasCountry + "_admin_areas_search"}
                    className="govuk-fieldset__legend filter-items__label filter-group__label govuk-!-width-full govuk-!-margin-bottom-0"
                >
                    {getCountryName(adminAreasCountry)} admin area
                    <div className="govuk-!-padding-top-1 govuk-!-margin-bottom-1 govuk-body">
                        <TypeAhead
                            inputId={"admin_areas_" + adminAreasCountry}
                            containerClasses="govuk-!-width-full"
                            options={adminAreas[adminAreasCountry]}
                            onChange={(event) =>
                                props.handleChangeFunction(
                                    event,
                                    adminAreasCountry,
                                )
                            }
                            placeholder="Search admin area"
                            defaultValue={getDefaultValue(
                                adminAreas[adminAreasCountry],
                                adminAreasCountry,
                            )}
                        />
                    </div>
                </div>
            ))}
        </div>
    );
}

function LocationFilter(props) {
    const tradingBlocIds = props.tradingBlocs.map(
        (tradingBloc) => tradingBloc.value,
    );

    const initialSelectedLocations = props.countries.reduce(
        (selected, location) => {
            if (location.checked) selected.push(location);
            return selected;
        },
        [],
    );
    const initialSelectedLocationIds = initialSelectedLocations.map(
        (location) => location.value,
    );
    const [selectedLocationIds, setSelectedLocationIds] = useState(
        initialSelectedLocationIds,
    );

    const handleLocationSelect = (value, meta) => {
        if (meta.action == "select-option") {
            let location = meta.option.value;
            setSelectedLocationIds(selectedLocationIds.concat(location));
        } else {
            let location = meta.removedValue.value;
            setSelectedLocationIds(
                selectedLocationIds.filter((item) => item !== location),
            );
            // Must also clear the child admin areas if country is removed
            if (selectedAdminAreaIds[location]) {
                selectedAdminAreaIds[location] = [];
            }
        }
    };

    const getTradingBlocLabel = (tradingBloc) => {
        return (
            {
                TB00003: "Include ASEAN-wide barriers",
                TB00016: "Include EU-wide barriers",
                TB00017: "Include GCC-wide barriers",
                TB00013: "Include EAEU-wide barriers",
                TB00026: "Include Mercosur-wide barriers",
            }[tradingBloc.code] || "Include " + tradingBloc.name + " barriers"
        );
    };

    const validAdminAreaIds = [];
    for (let i = 0; i < props.adminAreasCountries.length; i++) {
        validAdminAreaIds.push(props.adminAreasCountries[i]["id"]);
    }

    const selectedAdminAreaCountryIds = selectedLocationIds.reduce(
        (selected, location) => {
            if (validAdminAreaIds.includes(location)) selected.push(location);
            return selected;
        },
        [],
    );

    const selectedTradingBlocIds = selectedLocationIds.reduce(
        (selected, location) => {
            if (tradingBlocIds.includes(location)) selected.push(location);
            return selected;
        },
        [],
    );

    const selectedCountryTradingBlocs = props.tradingBlocData.reduce(
        (selected, tradingBloc) => {
            if (
                selectedLocationIds.some((item) =>
                    tradingBloc.country_ids.includes(item),
                )
            )
                selected.push(tradingBloc);
            return selected;
        },
        [],
    );

    const selectedCountryTradingBlocsCodes = props.tradingBlocData.map(
        (tradingBloc) => tradingBloc.code,
    );
    const initialExtraLocation = new URLSearchParams(
        window.location.search,
    ).getAll("extra_location");

    const initialSelectedTradingBlocValues = props.tradingBlocData.reduce(
        (selected, tradingBloc) => {
            return {
                ...selected,
                [tradingBloc.code]: initialExtraLocation.includes(
                    tradingBloc.code,
                ),
            };
        },
        {},
    );

    const [selectedAllTradingBlocks, setSelectedAllTradingBlocks] =
        useState(false);
    const [
        selectedCountryTradingBlocValues,
        setSelectedCountryTradingBlocValues,
    ] = useState(initialSelectedTradingBlocValues);

    const individualTradingBlockChangeHandler = (event, tradingBloc) => {
        const value = event.target.checked;
        setSelectedCountryTradingBlocValues({
            ...selectedCountryTradingBlocValues,
            [tradingBloc.code]: value,
        });
        setSelectedAllTradingBlocks(false);
    };

    const allTradingBlocsChangeHandler = (event) => {
        const value = event.target.checked;
        if (!value) {
            setSelectedAllTradingBlocks(false);
        } else {
            setSelectedAllTradingBlocks(true);
            setSelectedCountryTradingBlocValues(
                selectedCountryTradingBlocsCodes.reduce(
                    (values, tradingBlocCode) => {
                        return {
                            ...values,
                            [tradingBlocCode]: true,
                        };
                    },
                    {},
                ),
            );
        }
    };

    const initialSelectedAdminAreaValues = () => {
        // Get the requested admin areas from the GET request parameters
        const queryString = window.location.search;
        const urlParams = new URLSearchParams(queryString);
        const admin_areas = urlParams.get("admin_areas");

        if (admin_areas && selectedLocationIds.length) {
            // If there are admin_areas in the request, format the URL parameter to a JS object
            // Skip over this if there are no countries selected.
            var admin_areas_formatted = JSON.parse(admin_areas);
            return admin_areas_formatted;
        } else {
            // If there are not admin_areas, create an empty object with the correct key structure
            const selectedAdminAreaIds = {};
            for (let i = 0; i < props.adminAreasCountries.length; i++) {
                selectedAdminAreaIds[props.adminAreasCountries[i]["id"]] = [];
            }
            return selectedAdminAreaIds;
        }
    };

    const [selectedAdminAreaIds, setselectedAdminAreaIds] = useState(
        initialSelectedAdminAreaValues,
    );

    const handleAdminAreaSelect = (event, country) => {
        var selectedAreasList = [];
        for (let i = 0; i < event.length; i++) {
            selectedAreasList.push(event[i]["value"]);
        }
        selectedAdminAreaIds[country] = selectedAreasList;
        document.getElementById("admin_areas").value =
            JSON.stringify(selectedAdminAreaIds);
    };

    return (
        <div className="govuk-form-group">
            <fieldset className="govuk-fieldset">
                <legend className="govuk-fieldset__legend filter-items__label filter-group__label visually-hidden">
                    {props.label}
                </legend>

                <label
                    className="govuk-label filter-items__label"
                    htmlFor="location"
                >
                    {props.label}
                </label>

                <TypeAhead
                    inputId="location"
                    options={props.countries}
                    name="country"
                    onChange={handleLocationSelect}
                    placeholder="Search locations"
                    defaultValue={initialSelectedLocations}
                />

                {selectedTradingBlocIds.length ? (
                    <TradingBlocFilter
                        tradingBlocs={props.tradingBlocs}
                        selectedTradingBlocIds={selectedTradingBlocIds}
                    />
                ) : null}

                {selectedAdminAreaCountryIds.length ? (
                    <AdminAreaFilter
                        adminAreas={props.adminAreaData}
                        selectedAdminAreaCountryIds={
                            selectedAdminAreaCountryIds
                        }
                        selectedAdminAreaIds={selectedAdminAreaIds}
                        countryNames={props.adminAreasCountries}
                        handleChangeFunction={handleAdminAreaSelect}
                    />
                ) : null}

                {selectedCountryTradingBlocs.length ? (
                    <div className="checkbox-filter govuk-!-width-full">
                        {selectedCountryTradingBlocs.map(
                            (tradingBloc, index) => (
                                <div className="checkbox-filter__item" key={index}>
                                    <input
                                        className="checkbox-filter__input"
                                        id={"extra_location" + index}
                                        name="extra_location"
                                        type="checkbox"
                                        value={tradingBloc.code}
                                        checked={
                                            selectedCountryTradingBlocValues[
                                                tradingBloc.code
                                            ]
                                        }
                                        onChange={(event) =>
                                            individualTradingBlockChangeHandler(
                                                event,
                                                tradingBloc,
                                            )
                                        }
                                        // checked={selectedAllTradingBlocks || initialExtraLocation.includes(tradingBloc.code)}
                                    />
                                    <label
                                        className="govuk-label checkbox-filter__label"
                                        htmlFor={"extra_location" + index}
                                    >
                                        {getTradingBlocLabel(tradingBloc)}
                                    </label>
                                </div>
                            ),
                        )}
                        {/* {selectedCountryTradingBlocs.length > 0 ? (<div className="checkbox-filter__item"}>
                <input
                  className="checkbox-filter__input"
                  id={"extra_location" + selectedCountryTradingBlocs.length}
                  onChange={allTradingBlocsChangeHandler}
                  type="checkbox"
                  value={"ALL"}
                  checked={selectedAllTradingBlocks}
                />
                <label className="govuk-label checkbox-filter__label" for={"extra_location" + selectedCountryTradingBlocs.length}>
                  Include all trading blocks
                </label>
              </div>) : null}*/}
                    </div>
                ) : null}
            </fieldset>
        </div>
    );
}

export default LocationFilter;
