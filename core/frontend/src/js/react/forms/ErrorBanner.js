import React from "react";


function ErrorBanner(props) {
  return (
    <div class="govuk-error-summary restrict-width" aria-labelledby="error-summary-title" role="alert" tabindex="-1" data-module="error-summary">
        <h2 class="govuk-error-summary__title" id="error-summary-title">There is a problem</h2>
        <div class="govuk-error-summary__body">
            <ul class="govuk-list govuk-error-summary__list">
              <li><a href="#code">{props.message}</a></li>
            </ul>
        </div>
    </div>
  )
}


export default ErrorBanner;
