import React, { useEffect, useState } from "react";
import ReactDOM from "react-dom";
import { RadioInput } from "../partials/forms/RadioInput";
import { SelectInput } from "../partials/forms/SelectInput";
import { Heading } from "../partials/Heading";
import {
    AdminArea,
    Country,
    FieldChoice,
    FieldDescription,
    FieldOverrides,
    TradingBloc,
} from "../types";
import { SelectedAdminAreasBox } from "./SelectedAdminAreasBox";

interface LocationFormReactData<T> {
    barrier_id: string;
    method: string;
    heading: {
        caption: string;
        text: string;
    };
    form_data: T;
    form_errors?: {
        [key: string]: string[] | undefined;
    };
    csrf_token: string;
    form_fields: {
        [name: string]: FieldDescription;
    };
    countries: Country[];
    trading_blocs: TradingBloc[];
    admin_areas: AdminArea[];
}

interface LocationFormData {
    admin_areas: string[];
    caused_by_trading_bloc: string;
    has_admin_areas: string;
    location: string;
    country?: string;
    trading_bloc?: string;
}

const mapIdsToAdminAreas = (ids: string[], adminAreas: AdminArea[]) => {
    if (!ids || !adminAreas) {
        return [];
    }
    return ids.map((id) => {
        return adminAreas.find((area) => area.id === id);
    })
}

const TRADING_BLOC_TO_HELP_TEXT = {
    TB00016:
        "Yes should be selected if the barrier is a local application of an EU " +
        "regulation. If it is an EU-wide barrier, the country location should " +
        "be changed to EU in the location screen.",
    TB00026:
        "Yes should be selected if the barrier is a local application of an" +
        " Mercosur regulation. If it is an Mercosur-wide barrier, the country" +
        " location should be changed to Southern Common Market (Mercosur) in" +
        " the location screen.",
    TB00013:
        "Yes should be selected if the barrier is a local application of an" +
        " EAEU regulation. If it is an EAEU-wide barrier, the country location" +
        " should be changed to Eurasian Economic Union (EAEU) in the location" +
        " screen.",
    TB00017:
        "Yes should be selected if the barrier is a local application of an GCC" +
        " regulation. If it is an GCC-wide barrier, the country location should" +
        " be changed to Gulf Cooperation Council (GCC) in the location screen.",
};

const generateCausedByTradingblocLabel = (name: string) => {
    return `Was this barrier caused by a regulation introduced by the ${name}`;
};

const CAUSED_BY_TRADING_BLOC_OVERRIDES: {
    [trading_bloc: string]: FieldOverrides;
} = {
    TB00016: {
        label: generateCausedByTradingblocLabel("EU"),
        help_text: TRADING_BLOC_TO_HELP_TEXT["TB00016"],
    },
    TB00026: {
        label: generateCausedByTradingblocLabel("Mercosur"),
        help_text: TRADING_BLOC_TO_HELP_TEXT["TB00026"],
    },
    TB00013: {
        label: generateCausedByTradingblocLabel("EAEU"),
        help_text: TRADING_BLOC_TO_HELP_TEXT["TB00013"],
    },
    TB00017: {
        label: generateCausedByTradingblocLabel("GCC"),
        help_text: TRADING_BLOC_TO_HELP_TEXT["TB00017"],
    },
};

interface LocationFormState {
    location?: string;
    country?: string;
    tradingBloc?: string;
    causedByTradingBloc?: string;
    causedByAdminAreas?: string;
    selectedAdminAreas: AdminArea[];
}

export const LocationForm = () => {
    const [selectedAdminArea, setSelectedAdminArea] = useState<AdminArea>();

    const [formState, setFormState] = useState<LocationFormState>({
        location: "",
        selectedAdminAreas: [],
    });
    const [pageReactData, setPageReactData] = useState<LocationFormReactData<LocationFormData>>();

    const {
        location,
        country,
        tradingBloc,
        causedByTradingBloc,
        causedByAdminAreas,
        selectedAdminAreas,
    } = formState;

    console.log("formState", formState);

    const data: LocationFormReactData<LocationFormData> = JSON.parse(
        document.getElementById("location-form-data").innerHTML
    );
    const csrf_token = document.querySelector<HTMLInputElement>(
        "[name=csrfmiddlewaretoken]"
    ).value;

    const {
        barrier_id,
        method,
        form_data,
        form_errors,
        form_fields,
        heading,
        countries,
        trading_blocs,
        admin_areas,
    } = data;

    useEffect(() => {
        setFormState({
            ...formState,
            location: form_data.location,
            country: isLocationACountry(form_data.location)
                ? form_data.location
                : undefined,
            tradingBloc: isLocationATradingBloc(form_data.location)
                ? form_data.location
                : undefined,
            causedByTradingBloc: form_data.caused_by_trading_bloc,
            causedByAdminAreas: form_data.has_admin_areas,
            selectedAdminAreas: mapIdsToAdminAreas(form_data.admin_areas, admin_areas),
        });
    }, []);

    // is location the id of an item in countries
    const isLocationACountry = (location: string) => {
        return countries.find((country) => country.id === location);
    };
    const isLocationATradingBloc = (location: string) => {
        return trading_blocs.find(
            (trading_bloc) => trading_bloc.code === location
        );
    };

    const getCountryTradingBloc = (country: string) => {
        return trading_blocs.find((trading_bloc) =>
            trading_bloc.country_ids.includes(country)
        );
    };

    const getCountryAdminAreas = (country: string) => {
        return admin_areas.filter((admin_area) => {
            return admin_area.country.id === country;
        });
    };

    const countryTradingBloc = country && getCountryTradingBloc(country);
    const causedByTradingBlocOverrides = countryTradingBloc
        ? CAUSED_BY_TRADING_BLOC_OVERRIDES[countryTradingBloc.code]
        : undefined;

    const countryAdminAreas = country && getCountryAdminAreas(country);
    const countryHasAdminAreas = country && countryAdminAreas.length > 0;

    const handleAddAdminArea = (event) => {
        event.preventDefault();
        const isAdminAreaAlreadyAdded = selectedAdminAreas.find(
            (area) => area.id === selectedAdminArea.id
        );
        if (!isAdminAreaAlreadyAdded) {
            setFormState({
                ...formState,
                selectedAdminAreas: [...selectedAdminAreas, selectedAdminArea],
            });
        }
        setSelectedAdminArea(null);
    };

    const onRemoveAdminArea = (area: AdminArea) => {
        const newSelectedAdminAreas = selectedAdminAreas.filter(
            (a) => a.id !== area.id
        );
        setFormState({
            ...formState,
            selectedAdminAreas: newSelectedAdminAreas,
        });
    };

    const onLocationChange = (value: string) => {
        console.log("onLocationChange", value);
        const newFormState = {
            location: value,
            country: "",
            tradingBloc: "",
            causedByTradingBloc: "",
            causedByAdminAreas: "",
            selectedAdminAreas: [],
        };
        if (isLocationACountry(value)) {
            setFormState({
                ...newFormState,
                country: value,
            });
        }
        if (isLocationATradingBloc(value)) {
            setFormState({
                ...newFormState,
                tradingBloc: value,
            });
        }
    };

    const onCausedByTradingBlocChange = (value: string) => {
        setFormState({
            ...formState,
            causedByTradingBloc: value,
        });
    };

    const onCausedByAdminAreasChange = (value: string) => {
        setFormState({
            ...formState,
            causedByAdminAreas: value,
        });
    };

    const countryChoices: FieldChoice[] = countries.map((country) => ({
        value: country.id,
        label: country.name,
        optGroup: "Countries",
    }));

    const tradingBlocChoices: FieldChoice[] = trading_blocs.map(
        (trading_bloc) => ({
            value: trading_bloc.code,
            label: trading_bloc.name,
            optGroup: "Trading Blocs",
        })
    );

    const locationChoices: FieldChoice[] = [
        ...tradingBlocChoices,
        ...countryChoices,
    ];

    const showCausedByTradingBloc = !!countryTradingBloc
    const showAdminAreasSelection = showCausedByTradingBloc ? (
        countryHasAdminAreas && causedByTradingBloc
    ) : ( countryHasAdminAreas)

    return (
        <div>
                <input
                    type="hidden"
                    name="csrfmiddlewaretoken"
                    value={csrf_token}
                />
                <div className="govuk-form-group">
                    <SelectInput
                        value={location}
                        field={form_fields.location}
                        overriddenChoices={locationChoices}
                        placeholder="Choose a location"
                        onChange={(value) => onLocationChange(value)}
                    />
                </div>

                {countryTradingBloc && causedByTradingBlocOverrides && (
                    <div className="govuk-form-group">
                        <RadioInput
                            value={causedByTradingBloc}
                            field={form_fields.caused_by_trading_bloc}
                            fieldOverrides={causedByTradingBlocOverrides}
                            onChange={(value) =>
                                onCausedByTradingBlocChange(value)
                            }
                            fieldErrors={form_errors?.caused_by_trading_bloc}
                        />
                    </div>
                )}
                {showAdminAreasSelection && (
                    <div className="govuk-form-group">
                        <RadioInput
                            value={causedByAdminAreas}
                            field={form_fields.has_admin_areas}
                            onChange={(value) =>
                                onCausedByAdminAreasChange(value)
                            }
                            fieldErrors={form_errors?.has_admin_areas}
                        />
                    </div>
                )}
                {causedByAdminAreas == "2" && (
                    <div className="govuk-form-group">
                        <SelectInput
                            value={selectedAdminArea?.id}
                            field={form_fields.admin_areas}
                            overriddenChoices={countryAdminAreas.map(
                                (admin_area) => ({
                                    value: admin_area.id,
                                    label: admin_area.name,
                                })
                            )}
                            placeholder="Choose an admin area"
                            onChange={(value) =>
                                setSelectedAdminArea(
                                    countryAdminAreas.find(
                                        (admin_area) => admin_area.id === value
                                    )
                                )
                            }
                        />
                        <div style={{ width: "100%", height: 12 }}></div>
                        <button
                            className="govuk-button button--secondary"
                            onClick={handleAddAdminArea}
                        >
                            Add admin area
                        </button>

                        {selectedAdminAreas.length > 0 && (
                            <SelectedAdminAreasBox
                                selectedAdminAreas={selectedAdminAreas}
                                onRemove={onRemoveAdminArea}
                                field={form_fields.admin_areas}
                            />
                        )}
                    </div>
                )}

                <div className="{% form_group_classes form.errors %}"></div>
        </div>
    );
};

const LOCATION_FORM_CONTAINER_ID = "location-form-container";

export const renderLocationForm = () => {
    ReactDOM.render(
        <LocationForm />,
        document.getElementById(LOCATION_FORM_CONTAINER_ID)
    );
};
