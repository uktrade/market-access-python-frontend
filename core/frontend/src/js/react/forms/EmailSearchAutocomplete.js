import React from "react";
import {
    useQuery,
    QueryClient,
    QueryClientProvider,
} from "@tanstack/react-query";

import Downshift from "downshift";

function EmailSearchAutocomplete({ field, label }) {
    const initialInputValue = field.value,
        initialFieldClasses = field.className,
        initialFieldName = field.name,
        initialLabelClasses = label.className,
        initialLabelText = label.innerText;

    const queryClient = new QueryClient();

    const itemToString = (item) => {
        return item ? item.email : "";
    };

    const searchUsers = async (/** @type {any} */ query) => {
        const response = await fetch(`/users/search/?q=${query}`);
        const data = await response.json();
        return data.results;
    };

    const AutocompleteMenu = ({
        inputValue,
        getMenuProps,
        getItemProps,
        highlightedIndex,
    }) => {
        const query = useQuery(["users", inputValue], async () => {
            const data = await searchUsers(inputValue);
            return data;
        });
        return query.data ? (
            <ul
                {...getMenuProps({
                    className: "dmas-autocomplete__suggestions govuk-list",
                })}
            >
                {query.data.map((item, index) => (
                    <li
                        key={`${item.email}`}
                        {...getItemProps({
                            key: item.email,
                            item,
                            index,
                            className: [
                                "mentions-item",
                                "dmas-autocomplete__suggestions__item",
                                highlightedIndex === index ? "focused" : "",
                            ].join(" "),
                        })}
                    >
                        <div className={"dmas-autocomplete__name"}>
                            {[item.first_name, item.last_name].join(" ")}
                        </div>
                        {item.email}
                    </li>
                ))}
            </ul>
        ) : (
            <ul
                {...getMenuProps({
                    className: "dmas-autocomplete__suggestions govuk-list",
                })}
            ></ul>
        );
    };

    const AutocompleteContent = () => {
        return (
            <Downshift
                itemToString={itemToString}
                inputId={field.id}
                initialInputValue={initialInputValue}
            >
                {({
                    getInputProps,
                    getItemProps,
                    getLabelProps,
                    getMenuProps,
                    isOpen,
                    inputValue,
                    highlightedIndex,
                    getRootProps,
                }) => (
                    <div>
                        <label
                            {...getLabelProps({
                                className: initialLabelClasses,
                            })}
                        >
                            {initialLabelText}
                        </label>
                        <div {...getRootProps({}, { suppressRefError: true })}>
                            <input
                                {...getInputProps({
                                    className: initialFieldClasses,
                                    name: initialFieldName,
                                })}
                            />
                        </div>
                        {isOpen ? (
                            <AutocompleteMenu
                                inputValue={inputValue}
                                getMenuProps={getMenuProps}
                                getItemProps={getItemProps}
                                highlightedIndex={highlightedIndex}
                            />
                        ) : null}
                    </div>
                )}
            </Downshift>
        );
    };

    return (
        <QueryClientProvider client={queryClient}>
            <AutocompleteContent />
        </QueryClientProvider>
    );
}

export default EmailSearchAutocomplete;
