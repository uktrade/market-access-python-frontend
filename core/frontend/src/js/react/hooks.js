import React from "react";

export const useWindowQueryParams = () => {
    // Initialize our `search` state from the current location
    const [search, setSearch] = React.useState(() => window.location.search);

    React.useEffect(() => {
        // Handler to sync our state with the real URL `search` value
        const handleLocationChange = () => {
            const newSearch = window.location.search;
            // Update state only if the search string has actually changed
            setSearch((prevSearch) =>
                prevSearch !== newSearch ? newSearch : prevSearch,
            );
        };

        // Store references to original methods so we can restore later
        const originalPushState = history.pushState;
        const originalReplaceState = history.replaceState;

        // Monkey-patch pushState
        history.pushState = function (...args) {
            originalPushState.apply(this, args);
            handleLocationChange();
        };

        // Monkey-patch replaceState
        history.replaceState = function (...args) {
            originalReplaceState.apply(this, args);
            handleLocationChange();
        };

        // Listen for back/forward navigation
        window.addEventListener("popstate", handleLocationChange);

        // Cleanup on unmount
        return () => {
            history.pushState = originalPushState;
            history.replaceState = originalReplaceState;
            window.removeEventListener("popstate", handleLocationChange);
        };
    }, []);

    // Memoize the URLSearchParams object so it doesn't get re-created on each render
    return React.useMemo(() => new URLSearchParams(search), [search]);
};
