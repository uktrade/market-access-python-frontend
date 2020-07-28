import React from "react";


function CodeBox(props) {
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


function CodeInput(props) {
  const boxCount = props.boxCount || 5
  return (
    <div className="govuk-form-group commodity-code-form-group">
      {[...Array(boxCount)].map((x, index) =>
        <CodeBox
          index={index}
          onChange={props.onChange}
          onPaste={props.onPaste}
          refContainer={props.refContainer}
          disabled={props.disabled(index)}
        />
      )}
    </div>
  )
}


export default CodeInput
