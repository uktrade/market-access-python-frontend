import React from "react"
import Select, { components } from 'react-select'
import {
    GDS_TRANSPORT_FONT,
    SCREEN_READER_CLASSES
} from "../constants"
import {
    BLACK,
    BLUE,
    GREY_2,
    GREY_3,
    RED,
    WHITE,
    YELLOW,
} from 'govuk-colours'


const customStyles = {
    option: (provided, state) => {
        let styles = {
            ...provided,
            "border-bottom": `1px solid ${GREY_2}`,
            "padding": "12px",
            ":hover": {
                "background-color": BLUE,
                "color": WHITE,
            },
        }
        if (state.isFocused) {
            styles.backgroundColor = BLUE
            styles.color = WHITE
        }
        return styles
    },
    control: (provided, state) => {
        let styles = {
            ...provided,
            "border": `2px solid ${BLACK}`,
            "border-radius": 0,
            "boxShadow": "none",
            ":hover": {
                "border": `2px solid ${BLACK}`,
            },
            ":focus": {
                "border": `2px solid ${BLACK}`,
            },
        }
        if (state.isFocused) styles["outline"] = `3px solid ${YELLOW}`
        return styles
    },
    valueContainer: (provided, state) => {
        return {
            ...provided,
            "padding": "4px 4px 2px",
        }
    },
    multiValue: (provided, state) => {
        return {
            ...provided,
            "font-size": "16px",
            "background-color": GREY_3,
            "border-radius": 0,
            "font-family": GDS_TRANSPORT_FONT,
        }
    },
    multiValueRemove: (provided, state) => {
        return {
            ...provided,
            ":hover": {
                "color": RED,
                "background-color": GREY_2,
                "border-radius": 0,
                "cursor": "pointer",
            },
        }
    },
    menu: (provided, state) => {
        return {
            ...provided,
            "margin": 0,
        }
    },
    menuList: (provided, state) => {
        return {
            ...provided,
            "border": `1px solid ${BLACK}`,
            "padding": 0,
            "margin-top": "-1px",
        }
    },
}

const Placeholder = props => {
  return <components.Placeholder
      {...props}
      className={"multiselect__placeholder"}
  />;
};

const Option = props => {
  return (
        <components.Option
            {...props}
            children={
                <div>
                    <span className={SCREEN_READER_CLASSES}>
                        {`Select option to add ${props.label} to barrier ${props.selectProps.inputId} filters.`}
                    </span>
                    <span className={"option-label"}>
                        {props.label}
                    </span>
                </div>
            }
        />
  );
};


function TypeAhead(props) {
    // In case you need to inspect the dropdown items use  menuIsOpen={true}
    // in props to keep the dropdown constantly open
    // that way it's easier to inspect individual items or the full list
    return (
        <Select
            {...props}
            isMulti={true}
            isClearable={false}
            className={`multiselect ${props.containerClasses}`}
            styles={customStyles}
            components={{
                IndicatorSeparator: () => null,
                Option: Option,
                Placeholder: Placeholder,
            }}
        />
    )
}

export default TypeAhead
