import React, { useEffect, useRef, useState } from "react"

import CommodityList from "./CommodityList"
import CountryInput from "./CountryInput"
import ErrorBanner from "../forms/ErrorBanner"


function TextArea(props) {
  return (
    <div className="govuk-form-group">
      <textarea className="govuk-textarea govuk-!-margin-bottom-0" name={props.fieldName} rows="5" defaultValue={props.defaultValue} onChange={props.onChange}></textarea>
    </div>
  )
}


function CodePairInput(props) {
  return (
    <input
      className="govuk-input govuk-input--width-2 commodity-code-input"
      name={"code_" + props.index}
      type="number"
      maxlength="2"
      ref={el => props.refContainer.current[props.index] = el}
      onChange={event => {
        props.onChange(event, props.index)
      }}
      onPaste={props.onPaste}
      disabled={props.disabled}
    />
  )
}


function CommodityForm(props) {
  const [codePairs, setCodePairs] = useState(["", "", "", "", "", ""])
  const [countryId, setCountryId] = useState(props.countries[0]["id"])
  const [confirmedCommodities, setConfirmedCommodities] = useState(props.confirmedCommodities)
  const [unconfirmedCommodities, setUnconfirmedCommodities] = useState([])
  const [pastedCodes, setPastedCodes] = useState("")
  const [codeLookupError, setCodeLookupError] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const boxCount = 5
  const inputRefContainer = useRef(new Array(boxCount))

  const handleCodeChange = (event, index) => {
    let newCodePairs = codePairs
    newCodePairs[index] = event.target.value
    setCodePairs(newCodePairs)
    let code = getCode()
    lookupCode(code)

    if (event.target.value.length >=2 && (index + 1) < boxCount) {
      inputRefContainer.current[index + 1].removeAttribute("disabled")
      inputRefContainer.current[index + 1].focus()
    }
  }

  const handleCountryChange = (event) => {
    setCountryId(event.target.value)
  }

  useEffect(() => {
    if (pastedCodes) {
      lookupMultipleCodes(pastedCodes)
    } else {
      let code = getCode()
      lookupCode(code)
    }
  }, [countryId]);

  const onCodePaste = (event, index) => {
    let codes = event.clipboardData.getData("Text")
    setPastedCodes(codes)
    lookupMultipleCodes(codes)
  }

  const onTextAreaChange = (event, index) => {
    lookupMultipleCodes(event.target.value)
  }

  const isBoxDisabled = (index) => {
    if (index == 0) return false
    for (let i = index - 1; i >= 0; i--) {
      if (codePairs[i] == "") return true
    }
    return false
  }

  const getCode = () => {
    let cleanedCodePairs = codePairs.map((element) => ("00" + element).slice(-2))
    let zeroPaddedCode = cleanedCodePairs.slice(0, 10).join("")
    return zeroPaddedCode.replace(/0+$/g, '')
  }

  const confirmCommodity = (event, index) => {
    confirmedCommodities.push(unconfirmedCommodities[index])
    setConfirmedCommodities([...confirmedCommodities])
    unconfirmedCommodities.splice(index, 1)
    setUnconfirmedCommodities([...unconfirmedCommodities])
  }

  const confirmAll = (event) => {
    setConfirmedCommodities(confirmedCommodities.concat(unconfirmedCommodities))
    setUnconfirmedCommodities([])
  }

  const removeCommodity = (event, index) => {
    confirmedCommodities.splice(index, 1)
    setConfirmedCommodities([...confirmedCommodities])
  }

  async function lookupCode(code) {
    if (code == "") return
    setIsLoading(true)
    let url = "?code=" + code + "&country=" + countryId
    const response = await fetch(url, {
      headers: {
        "X-Requested-With": "XMLHttpRequest"
      }
    })
    .then(res => res.json())
    .then(
      (result) => {
        setIsLoading(false)
        if (result["status"] == "ok") {
          let zeroPaddedCode = code.padEnd(10, "0")
          if (confirmedCommodities.some(commodity => commodity.code === zeroPaddedCode)) {
            setUnconfirmedCommodities([])
          } else {
            setUnconfirmedCommodities([result.data])
          }
          setCodeLookupError(null)
        } else {
          setUnconfirmedCommodities([])
          setCodeLookupError(result.message)
        }
      },
      (error) => {
        setIsLoading(false)
        setUnconfirmedCommodities([])
        setCodeLookupError(error)
      }
    )
  }

  async function lookupMultipleCodes(codes) {
    setIsLoading(true)
    codes = codes.replace(/[^\d+,;]/g, '').replace(";", ",").replace(/,+$/g, '').replace(/^,+/g, '')
    if (codes == "") return
    let url = "?codes=" + codes + "&country=" + countryId
    const response = await fetch(url, {
      headers: {
        "X-Requested-With": "XMLHttpRequest"
      }
    })
    .then(res => res.json())
    .then(
      (result) => {
        setIsLoading(false)
        if (result["status"] == "ok") {
          let filteredCommodities = result.data.filter(item => {
            return item && !confirmedCommodities.some(commodity => commodity.code === item.code)
          })
          setUnconfirmedCommodities(filteredCommodities)
          setCodeLookupError(null)
        } else {
          setUnconfirmedCommodities([])
          setCodeLookupError(result.message)
        }
      },
      (error) => {
        setIsLoading(false)
        setUnconfirmedCommodities([])
        setCodeLookupError(error)
      }
    )
  }

  return (
    <div className="restrict-width">
      {codeLookupError ? (
        <ErrorBanner message={codeLookupError} />
      ) : null}

      <form action="" method="POST">
        <div id="" className={codeLookupError ? "govuk-form-group govuk-form-group--error" : "govuk-form-group"}>
          <fieldset className="govuk-fieldset">
            <legend className="govuk-fieldset__legend govuk-fieldset__legend--s">{props.label}</legend>
            <span className="govuk-hint">{props.helpText}</span>

            <CountryInput countries={props.countries} countryId={countryId} onChange={handleCountryChange} />

            {codeLookupError ? (
              <span class="govuk-error-message">
                <span class="govuk-visually-hidden">Error:</span>
                {codeLookupError}
              </span>
            ) : null}

            {pastedCodes ? (
              <TextArea fieldName="codes" defaultValue={pastedCodes} onChange={onTextAreaChange} />
            ) : (
              <div className="govuk-form-group commodity-code-form-group">
                {[...Array(boxCount)].map((x, index) =>
                  <CodePairInput
                    index={index}
                    onChange={handleCodeChange}
                    onPaste={onCodePaste}
                    refContainer={inputRefContainer}
                    disabled={isBoxDisabled(index)}
                  />
                )}
              </div>
            )}
          </fieldset>
        </div>
      </form>

      <p class="govuk-body">Need help? <a href="">Look up codes</a></p>

      {unconfirmedCommodities.length ? (
        <CommodityList confirmed={false} commodities={unconfirmedCommodities} onClick={confirmCommodity} />
      ) : null}

      {unconfirmedCommodities.length > 1 ? (
          <button
            name="confirm-all"
            className="commodities-list__confirm-all govuk-button govuk-button--secondary"
            data-module="govuk-button"
            onClick={confirmAll}>
            Confirm all
          </button>
      ) : null}

      {confirmedCommodities.length ? (
        <h3 className="commodities-list__title">HS commodity codes to add to this barrier</h3>
      ) : null}

      {confirmedCommodities.length ? (
        <CommodityList confirmed={true} commodities={confirmedCommodities} onClick={removeCommodity} />
      ) : null}

      <span className="govuk-hint govuk-!-margin-bottom-6">Descriptions are only shown for codes up to HS6.</span>

      <form action="" method="POST">
        <input type="hidden" name="csrfmiddlewaretoken" value={props.csrfToken} />
        {confirmedCommodities.map((commodity, index) =>
          <input type="hidden" name="codes" value={commodity.code} />
        )}
        {confirmedCommodities.map((commodity, index) =>
          <input type="hidden" name="countries" value={commodity.country.id} />
        )}
        <button name="action" value="save" class="govuk-button" data-module="govuk-button">Done</button>
        <button class="form-cancel govuk-button button-as-link" name="action" value="cancel">Cancel</button>
      </form>

    </div>
  )
}


export default CommodityForm
