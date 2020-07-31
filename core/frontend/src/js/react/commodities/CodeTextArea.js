import React from "react";


function CodeTextArea(props) {
  return (
    <div className="govuk-form-group">
      <textarea className="govuk-textarea govuk-!-margin-bottom-0" name={props.fieldName} rows="5" defaultValue={props.defaultValue} onChange={props.onChange}></textarea>
    </div>
  )
}


export default CodeTextArea
