import React from "react"

import Select from 'react-select'


const customStyles = {
  option: (provided, state) => ({
    "border-bottom": "1px solid #b1b4b6",
    "padding": "12px",
    ":hover": {
      "background-color": "#006eb1",
      "color": "#fff",
    },
  }),
  control: (provided, state) => {
    return {
      ...provided,
      "border": "2px solid black",
      "border-radius": 0,
      "boxShadow": "none",
      ":focus": {
        "outline": "3px solid #fd0 !important",
      },
      ":hover": {
        "border": "2px solid black",
      },
    }
  },
  multiValue: (provided, state) => {
    return {
      ...provided,
      "font-size": "16px",
      "background-color": "#f3f2f1",
      "border-radius": 0,
      "font-family": '"GDS Transport",Arial,sans-serif'
    };
  },
  multiValueRemove: (provided, state) => {
    return {
      ...provided,
      ":hover": {
        "color": "#d4351c",
        "background-color": "#b1b4b6",
        "border-radius": 0,
        "cursor": "pointer",
      },
    };
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
      "border": "1px solid black",
      "padding": 0,
    }
  },
  placeholder: (provided, state) => {
    return {
      ...provided,
      "font-family": '"GDS Transport",Arial,sans-serif',
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
      styles={customStyles}
      components={{
        IndicatorSeparator: () => null
      }}
    />
  )
}

export default TypeAhead
