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
    return (
        <>
            {errors.map((error, index) => {
                return <FieldError key={index} error={error} />;
            })}
        </>
    );
};
