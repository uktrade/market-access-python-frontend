import React from "react";

const codeBoxLabels = {
    0: "First",
    1: "Second",
    2: "Third",
    3: "Fourth",
    4: "Fifth",
};

function CodeBox(props) {
    return (
        <div className="codebox__container">
            <label
                className="sr-only govuk-visually-hidden"
                htmlFor={"code_" + props.index}
            >
                {codeBoxLabels[props.index] +
                    " two digits of your HS commodity code."}
            </label>
            <input
                id={"code_" + props.index}
                className="govuk-input govuk-input--width-2 commodity-code-input"
                name={"code_" + props.index}
                type="number"
                maxLength="2"
                inputMode="numeric"
                pattern="[0-9]{2}"
                ref={(el) => (props.refContainer.current[props.index] = el)}
                onChange={(event) => {
                    props.onChange(event, props.index);
                }}
                onPaste={props.onPaste}
                disabled={props.disabled}
            />
        </div>
    );
}

function CodeInput(props) {
    const boxCount = props.boxCount || 5;
    return (
        <div className="govuk-form-group commodity-code-form-group">
            {[...Array(boxCount)].map((x, index) => (
                <CodeBox
                    index={index}
                    onChange={props.onChange}
                    onPaste={props.onPaste}
                    refContainer={props.refContainer}
                    disabled={props.disabled(index)}
                />
            ))}
        </div>
    );
}

export default CodeInput;
