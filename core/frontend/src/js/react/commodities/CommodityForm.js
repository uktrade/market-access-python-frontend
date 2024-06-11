import React, { useEffect, useRef, useState } from "react";

import CodeInput from "./CodeInput";
import CodeTextArea from "./CodeTextArea";
import CommodityList from "./CommodityList";
import LocationInput from "./LocationInput";
import ErrorBanner from "../forms/ErrorBanner";

function CommodityForm(props) {
    const [codeArray, setCodeArray] = useState(["", "", "", "", ""]);
    const [locationId, setLocationId] = useState(props.locations[0]["id"]);
    const [confirmedCommodities, setConfirmedCommodities] = useState(
        props.confirmedCommodities
    );
    const [unconfirmedCommodities, setUnconfirmedCommodities] = useState([]);
    const [pastedCodes, setPastedCodes] = useState("");
    const [codeLookupError, setCodeLookupError] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const boxCount = 5;
    const inputRefContainer = useRef(new Array(boxCount));

    const { isReportJourney, nextUrl, showActions } = props;

    const handleLocationChange = (event) => {
        setLocationId(event.target.value);
    };

    const handleCodeChange = (event, index) => {
        let newCodeArray = codeArray;
        newCodeArray[index] = event.target.value;
        setCodeArray(newCodeArray);
        let code = getCode();
        lookupCode(code);

        if (event.target.value.length >= 2 && index + 1 < boxCount) {
            inputRefContainer.current[index + 1].removeAttribute("disabled");
            inputRefContainer.current[index + 1].focus();
        }
    };

    const handleCodePaste = (event, index) => {
        let codes = event.clipboardData.getData("Text");
        setPastedCodes(codes);
        lookupMultipleCodes(codes);
    };

    const handleTextAreaChange = (event, index) => {
        lookupMultipleCodes(event.target.value);
    };

    useEffect(() => {
        if (pastedCodes) {
            lookupMultipleCodes(pastedCodes);
        } else {
            let code = getCode();
            lookupCode(code);
        }
    }, [locationId]);

    const clearCodeInput = () => {
        for (var input of inputRefContainer.current) {
            input.value = "";
        }
        setCodeArray(["", "", "", "", ""]);
    };

    const isBoxDisabled = (index) => {
        if (index == 0) return false;
        for (let i = index - 1; i >= 0; i--) {
            if (codeArray[i] == "") return true;
        }
        return false;
    };

    const getCode = () => {
        let cleanedCodeArray = codeArray.map((element) =>
            ("00" + element).slice(-2)
        );
        let zeroPaddedCode = cleanedCodeArray.slice(0, 10).join("");
        return zeroPaddedCode.replace(/0+$/g, "");
    };

    const confirmCommodity = (event, index) => {
        confirmedCommodities.push(unconfirmedCommodities[index]);
        setConfirmedCommodities([...confirmedCommodities]);
        unconfirmedCommodities.splice(index, 1);
        setUnconfirmedCommodities([...unconfirmedCommodities]);
        clearCodeInput();
    };

    const confirmAll = (event) => {
        setConfirmedCommodities(
            confirmedCommodities.concat(unconfirmedCommodities)
        );
        setUnconfirmedCommodities([]);
    };

    const removeCommodity = (event, index) => {
        confirmedCommodities.splice(index, 1);
        setConfirmedCommodities([...confirmedCommodities]);
    };

    async function lookupCode(code) {
        if (code == "") {
            setUnconfirmedCommodities([]);
            return;
        }
        setIsLoading(true);
        const url = "?code=" + code + "&location=" + locationId;
        const response = await fetch(url, {
            headers: {
                "X-Requested-With": "XMLHttpRequest",
            },
        })
            .then((res) => res.json())
            .then(
                (result) => {
                    setIsLoading(false);
                    if (result["status"] == "ok") {
                        let zeroPaddedCode = code.padEnd(10, "0");
                        if (
                            confirmedCommodities.some(
                                (commodity) => commodity.code === zeroPaddedCode
                            )
                        ) {
                            setUnconfirmedCommodities([]);
                        } else {
                            setUnconfirmedCommodities([result.data]);
                        }
                        setCodeLookupError(null);
                    } else {
                        setUnconfirmedCommodities([]);
                        setCodeLookupError(result.message);
                    }
                },
                (error) => {
                    setIsLoading(false);
                    setUnconfirmedCommodities([]);
                    setCodeLookupError(error);
                }
            );
    }

    async function lookupMultipleCodes(codes) {
        setIsLoading(true);
        codes = codes
            .replace(/[\r\n]+/g, ";")
            .replace(/[^\d+,;]/g, "")
            .replaceAll(";", ",")
            .replaceAll(",,", ",")
            .replace(/,+$/g, "")
            .replace(/^,+/g, "");
        if (codes == "") {
            setUnconfirmedCommodities([]);
            return;
        }
        const url = "?codes=" + codes + "&location=" + locationId;
        const response = await fetch(url, {
            headers: {
                "X-Requested-With": "XMLHttpRequest",
            },
        })
            .then((res) => res.json())
            .then(
                (result) => {
                    setIsLoading(false);
                    if (result["status"] == "ok") {
                        let newCommodities = result.data.filter((item) => {
                            return !confirmedCommodities.some(
                                (commodity) => commodity.code === item.code
                            );
                        });
                        setUnconfirmedCommodities(newCommodities);
                        setCodeLookupError(null);
                    } else {
                        setUnconfirmedCommodities([]);
                        setCodeLookupError(result.message);
                    }
                },
                (error) => {
                    setIsLoading(false);
                    setUnconfirmedCommodities([]);
                    setCodeLookupError(error);
                }
            );
    }

    return (
        <div className="restrict-width">
            {codeLookupError ? <ErrorBanner message={codeLookupError} /> : null}

            <form action="" method="POST">
                <div
                    id=""
                    className={
                        codeLookupError
                            ? "govuk-form-group govuk-form-group--error govuk-!-margin-bottom-0"
                            : "govuk-form-group govuk-!-margin-bottom-0"
                    }
                >
                    <fieldset className="govuk-fieldset">
                        <legend className="govuk-fieldset__legend govuk-fieldset__legend--s">
                            {props.label}
                        </legend>
                        <span className="govuk-hint">
                            HS codes help DBT analysts evaluate an prioritise
                            barriers.{" "}
                            <a
                                href="https://www.gov.uk/trade-tariff"
                                className="govuk-link"
                                target="_blank"
                                rel="noreferrer"
                            >
                                Find the right codes for your goods
                            </a>{" "}
                            if you aren&apos;t sure which to use. You can copy
                            and paste multiple codes separated by commas into
                            the first box.
                        </span>

                        <LocationInput
                            locations={props.locations}
                            locationId={locationId}
                            onChange={handleLocationChange}
                        />

                        {codeLookupError ? (
                            <span className="govuk-error-message">
                                <span className="govuk-visually-hidden">
                                    Error:
                                </span>
                                {codeLookupError}
                            </span>
                        ) : null}

                        {pastedCodes ? (
                            <CodeTextArea
                                fieldName="codes"
                                defaultValue={pastedCodes}
                                onChange={handleTextAreaChange}
                            />
                        ) : (
                            <CodeInput
                                onChange={handleCodeChange}
                                onPaste={handleCodePaste}
                                refContainer={inputRefContainer}
                                disabled={isBoxDisabled}
                            />
                        )}
                    </fieldset>
                </div>
            </form>

            {unconfirmedCommodities.length ? (
                <CommodityList
                    confirmed={false}
                    commodities={unconfirmedCommodities}
                    onClick={confirmCommodity}
                />
            ) : null}

            {unconfirmedCommodities.length > 1 ? (
                <button
                    name="confirm-all"
                    className="commodities-list__confirm-all govuk-button govuk-button--secondary"
                    data-module="govuk-button"
                    onClick={confirmAll}
                >
                    Confirm all
                </button>
            ) : null}

            {confirmedCommodities.length ? (
                <h3 className="commodities-list__title">
                    HS commodity codes to add to this barrier
                </h3>
            ) : null}

            {confirmedCommodities.length ? (
                <CommodityList
                    confirmed={true}
                    commodities={confirmedCommodities}
                    onClick={removeCommodity}
                />
            ) : null}

            {!isReportJourney ? (
                <form action="" method="POST">
                    <input
                        type="hidden"
                        name="csrfmiddlewaretoken"
                        value={props.csrfToken}
                    />
                    {confirmedCommodities.map((commodity, index) => (
                        <input
                            type="hidden"
                            name="codes"
                            value={commodity.code}
                        />
                    ))}
                    {confirmedCommodities.map((commodity, index) => {
                        if (commodity.country) {
                            return (
                                <input
                                    type="hidden"
                                    name="countries"
                                    value={commodity.country.id}
                                />
                            );
                        } else {
                            return (
                                <input
                                    type="hidden"
                                    name="countries"
                                    value=""
                                />
                            );
                        }
                    })}
                    {confirmedCommodities.map((commodity, index) => {
                        if (commodity.trading_bloc) {
                            return (
                                <input
                                    type="hidden"
                                    name="trading_blocs"
                                    value={commodity.trading_bloc.code}
                                />
                            );
                        } else {
                            return (
                                <input
                                    type="hidden"
                                    name="trading_blocs"
                                    value=""
                                />
                            );
                        }
                    })}

                    {nextUrl ? (
                        <div>
                            <button
                                type="submit"
                                className="govuk-button"
                                name="action"
                                value="save-and-go-to-summary"
                            >
                                Save
                            </button>
                            <a
                                href={nextUrl}
                                className="govuk-button button--secondary m-l-2"
                            >
                                Cancel
                            </a>
                        </div>
                    ) : null}

                    {/* {!nextUrl && isReportJourney && (

                    <div>

                        <button
                            name="action"
                            value="save"
                            className="govuk-button"
                            data-module="govuk-button"
                        >
                            Save and continue
                        </button>
                        <button
                            className="govuk-button button--secondary m-l-2"
                            name="action"
                            value="cancel"
                        >
                            Save and exit
                        </button>
                    </div>
                )} */}

                    {!nextUrl && !isReportJourney && (
                        <div>
                            <button
                                name="action"
                                value="save"
                                className="govuk-button govuk-!-margin-top-6 govuk-!-margin-right-2"
                                data-module="govuk-button"
                            >
                                Done
                            </button>
                            <button
                                className="govuk-button button--secondary govuk-!-margin-top-6"
                                name="action"
                                value="cancel"
                            >
                                Cancel
                            </button>
                        </div>
                    )}
                </form>
            ) : null}

            {isReportJourney ? (
                <div>
                    {confirmedCommodities.map((commodity, index) => (
                        <input
                            type="hidden"
                            name="barrier-export-type-codes"
                            value={commodity.code}
                        />
                    ))}
                    {confirmedCommodities.map((commodity, index) => {
                        if (commodity.country) {
                            return (
                                <input
                                    type="hidden"
                                    name="barrier-export-type-countries"
                                    value={commodity.country.id}
                                />
                            );
                        } else {
                            return (
                                <input
                                    type="hidden"
                                    name="countries"
                                    value="None"
                                />
                            );
                        }
                    })}
                    {confirmedCommodities.map((commodity, index) => {
                        if (commodity.trading_bloc) {
                            return (
                                <input
                                    type="hidden"
                                    name="barrier-export-type-trading_blocs"
                                    value={commodity.trading_bloc.code}
                                />
                            );
                        } else {
                            return (
                                <input
                                    type="hidden"
                                    name="trading_blocs"
                                    value="None"
                                />
                            );
                        }
                    })}
                </div>
            ) : null}
        </div>
    );
}

export default CommodityForm;
