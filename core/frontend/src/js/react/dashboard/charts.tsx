import React, {forwardRef, useState, useEffect} from "react";
import { render } from "react-dom";
import Charts from "react-apexcharts";
import ApexCharts from 'apexcharts';
import { parseIso } from "../utils";

const colorTheme = [
    "#d53880",
    "#003078",
    "#28a197",
    "#f47738",
    "#5694ca",
    "#4C2C92",
    "#6F72AF",
    "#F499BE",
    "#85994B",
    "#FFDD00",
]; // 10 GDS colours


interface ChartData {
    name: string;
    data: number[];
}

// Define interface for ref methods
export interface BarChartHandle {
    updateSeries: (newSeries: any[]) => void;
    resetSeries: () => void;
  }

export const useWindowQueryParams = () => {
// Initialize our `search` state from the current location
const [search, setSearch] = React.useState(() => window.location.search);

React.useEffect(() => {
    // Handler to sync our state with the real URL `search` value
    const handleLocationChange = () => {
    const newSearch = window.location.search;
    // Update state only if the search string has actually changed
    setSearch((prevSearch) => (prevSearch !== newSearch ? newSearch : prevSearch));
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
    window.addEventListener('popstate', handleLocationChange);

    // Cleanup on unmount
    return () => {
    history.pushState = originalPushState;
    history.replaceState = originalReplaceState;
    window.removeEventListener('popstate', handleLocationChange);
    };
}, []);

// Memoize the URLSearchParams object so it doesn't get re-created on each render
return React.useMemo(() => new URLSearchParams(search), [search]);
}

export const BarChart = forwardRef<BarChartHandle, {}>((_props, _ref) => {
    const queryParams = useWindowQueryParams();

    const [series, setSeries] = React.useState<ChartData[]>([
        {
            name: "Value of barriers estimated to be resolved",
            data: [],
        },
        {
            name: "Value of resolved barriers",
            data: [],
        },
    ]);

    const [options, setOptions] = useState<ApexCharts.ApexOptions>({
        chart: {
            type: 'bar'
        },
        series,
        title: {
            text: "Total value of open barriers estimated to be resolved and resolved barriers",
            align: "center",
        },
        noData: {
            text: 'Loading...'
        },
        xaxis: {
            categories: ["Loading ..."],
        },
        yaxis: {
            title: {
                text: "British pounds(£)",
            },
        },
        fill: {
            opacity: 1,
        },
        colors: colorTheme,
    });

    useEffect(() => {
        const filteredQueryParams = new URLSearchParams();
        queryParams.forEach((value, key) => {
          if (value) {
            filteredQueryParams.set(key, value);
          }
        });
        const queryString = filteredQueryParams.toString();
        const submitURL = `/dashboard-summary/?${queryString}`;

        const fetchData = async () => {
          try {
            const response = await fetch(submitURL, {
              headers: {
                "X-Requested-With": "XMLHttpRequest",
                "Content-Type": "application/json",
              },
            });
            const data = await response.json();

            setOptions((prevOptions) => ({
              ...prevOptions,
              noData: { text: 'Loading...' },
              xaxis: {
                categories: [
                  ` ${parseIso(data?.financial_year?.current_start)} to ${parseIso(data?.financial_year?.current_end)}`,
                ],
              },
            }));

            setSeries([
              {
                name: "Value of barriers estimated to be resolved",
                data: [data.barrier_value_chart.estimated_barriers_value || 0],
              },
              {
                name: "Value of resolved barriers",
                data: [data.barrier_value_chart.resolved_barriers_value || 0],
              },
            ]);
          } catch (error) {
            console.error(error);
          }
        };

        fetchData();
    }, [queryParams]);

    return <Charts options={options} series={series} type="bar" height={350} />;
});

export const renderBarChart = (elementId: string): void => {
    const element = document.getElementById(elementId);
    if (element) {
        render(<BarChart />, element);
    }
}
