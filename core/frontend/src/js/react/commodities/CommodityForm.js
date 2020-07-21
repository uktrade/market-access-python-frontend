import React, { useRef, useState } from "react";

import CommodityList from "./CommodityList"
import ErrorBanner from "../forms/ErrorBanner"


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
      disabled={props.disabled}
    />
  )
}


function CommodityForm(props) {
  const [codePairs, setCodePairs] = useState(["", "", "", "", "", ""])
  const [confirmedCommodities, setConfirmedCommodities] = useState(props.confirmedCommodities)
  const [unconfirmedCommodities, setUnconfirmedCommodities] = useState([])
  const [codeLookupError, setCodeLookupError] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const boxCount = 6
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
    return zeroPaddedCode.replace(/^|0+$/g, '')
  }

  const confirmCommodity = (event, index) => {
    confirmedCommodities.push(unconfirmedCommodities[index])
    setConfirmedCommodities([...confirmedCommodities])
    unconfirmedCommodities.splice(index, 1);
    setUnconfirmedCommodities([...unconfirmedCommodities])
  }

  const removeCommodity = (event, index) => {
    confirmedCommodities.splice(index, 1)
    setConfirmedCommodities([...confirmedCommodities])
  }

  async function lookupCode(code) {
    setIsLoading(true);
    let url = window.location.href + "?code=" + code
    const response = await fetch(url, {
      headers: {
        "X-Requested-With": "XMLHttpRequest"
      }
    })
    .then(res => res.json())
    .then(
      (result) => {
        setIsLoading(false);
        if (result["status"] == "ok") {
          setUnconfirmedCommodities([result.data]);
          setCodeLookupError(null);
        } else {
          setUnconfirmedCommodities([]);
          setCodeLookupError(result.message)
        }
      },
      (error) => {
        setIsLoading(false);
        setUnconfirmedCommodities([]);
        setCodeLookupError(error);
      }
    )
  }

  return (
    <div>
      {codeLookupError ? (
        <ErrorBanner message={codeLookupError} />
      ) : null}

      <form action="" method="POST" className="restrict-width">

        <div id="" className={codeLookupError ? "govuk-form-group govuk-form-group--error" : "govuk-form-group"}>
          <fieldset className="govuk-fieldset">
            <legend className="govuk-fieldset__legend govuk-fieldset__legend--s">Enter one or more HS commodity codes</legend>
            <span className="govuk-hint">Enter your HS code below ignoring any spaces or full stops. You can also copy and paste multiple codes separated by commas into the first box (there is no limit). Only numbers and commas will be recognised, all other punctuation and characters will be ignored.</span>

            {codeLookupError ? (
              <span class="govuk-error-message">
                <span class="govuk-visually-hidden">Error:</span>
                {codeLookupError}
              </span>
            ) : null}

            <div className="govuk-form-group commodity-code-form-group">
              {[...Array(boxCount)].map((x, index) =>
                <CodePairInput index={index} onChange={handleCodeChange} refContainer={inputRefContainer} disabled={isBoxDisabled(index)} />
              )}
            </div>
          </fieldset>
        </div>
      </form>

      <p class="govuk-body">Need help? <a href="">Look up codes</a></p>

      {unconfirmedCommodities.length ? (
        <CommodityList confirmed={false} commodities={unconfirmedCommodities} onClick={confirmCommodity} />
      ) : null}

      {confirmedCommodities.length ? (
        <h3>HS commodity codes to add to this barrier</h3>
      ) : null}

      {confirmedCommodities.length ? (
        <CommodityList confirmed={true} commodities={confirmedCommodities} onClick={removeCommodity} />
      ) : null}

      <form action="" method="POST">
        <input type="hidden" name="csrfmiddlewaretoken" value={props.csrfToken} />
        {confirmedCommodities.map((commodity, index) =>
          <input type="hidden" name="codes" value={commodity.code} />
        )}
        <button name="action" value="save" class="govuk-button" data-module="govuk-button">Done</button>
        <button class="form-cancel govuk-button button-as-link" name="action" value="cancel">Cancel</button>
      </form>

    </div>
  )
}


export default CommodityForm;
