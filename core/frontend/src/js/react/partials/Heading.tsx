import React from "react"

interface HeadingProps {
    caption: string;
    text: string;
}

export const Heading:React.FC<HeadingProps> = ({caption, text}) => {
    return (<h1 className="govuk-heading-l">
    <span className="govuk-caption-m js-heading-caption">{ caption }</span> { text }
  </h1>)
}
