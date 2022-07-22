import React, { useState } from "react";

import TypeAhead from "../forms/TypeAhead";

function TradingBlocFilter(props) {
    const selectedTradingBlocs = props.tradingBlocs.reduce(
        (selected, tradingBloc) => {
            if (props.selectedTradingBlocIds.includes(tradingBloc.value))
                selected.push(tradingBloc);
            return selected;
        },
        []
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

function LocationFilter(props) {
    const tradingBlocIds = props.tradingBlocs.map(
        (tradingBloc) => tradingBloc.value
    );
    const initialSelectedLocations = props.countries.reduce(
        (selected, location) => {
            if (location.checked) selected.push(location);
            return selected;
        },
        []
    );
    const initialSelectedLocationIds = initialSelectedLocations.map(
        (location) => location.value
    );
    const [selectedLocationIds, setSelectedLocationIds] = useState(
        initialSelectedLocationIds
    );

    const handleLocationSelect = (value, meta) => {
        if (meta.action == "select-option") {
            let location = meta.option.value;
            setSelectedLocationIds(selectedLocationIds.concat(location));
        } else {
            let location = meta.removedValue.value;
            setSelectedLocationIds(
                selectedLocationIds.filter((item) => item !== location)
            );
        }
    };

    const getTradingBlocLabel = (tradingBloc) => {
        return (
            {
                TB00016: "Include EU-wide barriers",
                TB00017: "Include GCC-wide barriers",
                TB00013: "Include EAEU-wide barriers",
                TB00026: "Include Mercosur-wide barriers",
            }[tradingBloc.code] || "Include " + tradingBloc.name + " barriers"
        );
    };

    const selectedTradingBlocIds = selectedLocationIds.reduce(
        (selected, location) => {
            if (tradingBlocIds.includes(location)) selected.push(location);
            return selected;
        },
        []
    );

    const selectedCountryTradingBlocs = props.tradingBlocData.reduce(
        (selected, tradingBloc) => {
            if (
                selectedLocationIds.some((item) =>
                    tradingBloc.country_ids.includes(item)
                )
            )
                selected.push(tradingBloc);
            return selected;
        },
        []
    );

    const selectedCountryTradingBlocsCodes = props.tradingBlocData.map(
        (tradingBloc) => tradingBloc.code
    );
    const initialExtraLocation = new URLSearchParams(
        window.location.search
    ).getAll("extra_location");

    const initialSelectedTradingBlocValues = props.tradingBlocData.reduce(
        (selected, tradingBloc) => {
            return {
                ...selected,
                [tradingBloc.code]: initialExtraLocation.includes(
                    tradingBloc.code
                ),
            };
        },
        {}
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
                    {}
                )
            );
        }
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

                {selectedCountryTradingBlocs.length ? (
                    <div className="checkbox-filter govuk-!-width-full">
                        {selectedCountryTradingBlocs.map(
                            (tradingBloc, index) => (
                                <div className="checkbox-filter__item">
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
                                                tradingBloc
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
                            )
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
