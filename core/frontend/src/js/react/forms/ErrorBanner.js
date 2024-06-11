import React from "react";

function ErrorBanner(props) {
    return (
        <div
            className="govuk-error-summary restrict-width"
            aria-labelledby="error-summary-title"
            role="alert"
            tabIndex="-1"
            data-module="error-summary"
        >
            <h2 className="govuk-error-summary__title" id="error-summary-title">
                There is a problem
            </h2>
            <div className="govuk-error-summary__body">
                <ul className="govuk-list govuk-error-summary__list">
                    <li>
                        <a href="#code">{props.message}</a>
                    </li>
                </ul>
            </div>
        </div>
    );
}

export default ErrorBanner;
