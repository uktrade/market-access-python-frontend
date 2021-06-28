// @ts-check
import React, { useState, useRef, useEffect } from 'react'
import { MentionsInput, Mention } from 'react-mentions'

function TextAreaWithMentions({
    textAreaName,
    textAreaId,
    preExistingText="",
    trigger="@",
    idPrefix="@",
    isSingleLine=false
}) {

    const mentionsRef = useRef()

    /** @type {[{x:number, y:number}, any]} */
    const [position, setPosition] = useState()

    /** @type {[string, any]} */
    const [noteText, setNoteText] = useState(preExistingText)

    /** @type {[string, any]} */
    const [tokenisedText, setTokenisedText] = useState(preExistingText)

    useEffect(() => {
        mentionsRef.current?.classList.add("govuk-textarea")
        console.log("mentionsRef", mentionsRef.current?.classList.add("govuk-textarea"))
        mentionsRef.current?.focus()
    }, [mentionsRef])

    const onTextChange = (event, newValue, newPlainTextValue, mentions) => {
        setNoteText(newPlainTextValue)
        setTokenisedText(newValue)
    }

    const searchUsers = async (/** @type {any} */ query) => {
        const response = await fetch(`/users/search/?q=${query}`)
        const data = await response.json()
        return data.results.map(item => ({
            id: `${idPrefix}${item.email}`,
            display: `${idPrefix}${item.email}`,
            email: item.email,
            firstName: item.first_name,
            lastName: item.last_name
        }))
    }

    const getSuggestions = async (query, callback) => {
        const users = await searchUsers(query)
        callback(users)
    }

    // react-mentions places some styling inline, so they need to be
    // overriden with the following style object
    const mentionsStyling = {
        suggestions: {
            marginTop: 35,
            item: {
                '&focused': {
                    backgroundColor: '#1d70b8',
                    color: 'white'
                },
            }
        }
    }

    return <div className="textarea-with-mentions">
        <MentionsInput
            value={tokenisedText}
            onChange={onTextChange}
            className="govuk-mentions"
            singleLine={isSingleLine}
            inputRef={mentionsRef}
            style={mentionsStyling}
        >
            <Mention
                trigger={trigger}
                data={getSuggestions}
                style={{ color: "#f47738", zIndex: 1, position: "relative", left: 1, top: 1 }}
                renderSuggestion={(suggestion, search, highlightedDisplay, index, focused) => {
                    const classNames = ["mentions-item"]
                    if (focused) {
                        classNames.push("focused")
                    }
                    return <div className={classNames.join(" ")}>
                        <div className={"mention-name"}>{suggestion.firstName} {suggestion.lastName}</div>
                        {suggestion.email}
                    </div>
                }}
            />
        </MentionsInput>
        <textarea id={textAreaId} name={textAreaName} value={noteText} style={{ display: 'none' }} />
    </div>
}

export default TextAreaWithMentions;
