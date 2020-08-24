import React from "react"

import Select from 'react-select'

import {GDS_TRANSPORT_FONT} from "../styles"
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
  option: (provided, state) => ({
    "border-bottom": `1px solid ${GREY_2}`,
    "padding": "12px",
    ":hover": {
      "background-color": BLUE,
      "color": WHITE,
    },
  }),
  control: (provided, state) => {
    let styles = {
      ...provided,
      "border": `2px solid ${BLACK}`,
      "border-radius": 0,
      "boxShadow": "none",
      ":hover": {
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
  placeholder: (provided, state) => {
    return {
      ...provided,
      "font-family": GDS_TRANSPORT_FONT,
      "font-size": "19px !important",
    }
  },
}


function TypeAhead(props) {
  return (
    <Select
      {...props}
      isMulti={true}
      isClearable={false}
      className="multiselect"
      styles={customStyles}
      components={{
        IndicatorSeparator: () => null
      }}
    />
  )
}

export default TypeAhead
