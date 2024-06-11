import React from "react";

interface FieldErrorProps {
    error: string;
}

export const FieldError: React.FC<FieldErrorProps> = ({ error }) => {
    return (
        <span className="govuk-error-message">
            <span className="govuk-visually-hidden">Error:</span>
            {error}
        </span>
    );
};

export const FieldErrorList: React.FC<{ errors: string[] }> = ({ errors }) => {
    // Field errors component matching Django's field error list template
    return (
        <>
            {errors.map((error, index) => {
                return <FieldError key={index} error={error} />;
            })}
        </>
    );
};
