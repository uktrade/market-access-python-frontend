import React, { useState, useEffect } from "react";

const RisksAndMitigationForm = (props) => {
    const [hasRisks, setHasRisks] = useState();

    const extraFormFieldsId = "extra-form-fields";
    const extraFormFields = document.getElementById(extraFormFieldsId);

    // get value of radio input with name 'has_risks'
    const getHasRisksValue = () => {
        const radioElements = document.getElementsByName("has_risks");
        for (let i = 0; i < radioElements.length; i++) {
            if (radioElements[i].checked) {
                setHasRisks(radioElements[i].value);
            }
        }
        console.log("hasRisks: " + hasRisks);
    };
    const handleHasRisksChange = (e) => {
        setHasRisks(e.target.value);
    };

    const updateFieldVisibility = () => {
        if (hasRisks === "YES") {
            extraFormFields.style.display = "block";
        } else {
            extraFormFields.style.display = "none";
        }
    };

    const addEventListenerToHasRisks = () => {
        const radioElements = document.getElementsByName("has_risks");
        for (let i = 0; i < radioElements.length; i++) {
            radioElements[i].addEventListener("change", handleHasRisksChange);
        }
    };

    useEffect(() => {
        getHasRisksValue();
        addEventListenerToHasRisks();
    }, []);

    useEffect(() => {
        updateFieldVisibility();
    }, [hasRisks]);

    return <div>{hasRisks}</div>;
};

export default RisksAndMitigationForm;
