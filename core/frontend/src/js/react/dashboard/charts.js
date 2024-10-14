import React from "react";
import Charts from "react-apexcharts";

import { normalizeValue } from "../utils";

const colorTheme = ["#d53880", "#003078", "#28a197", "#f47738", "#5694ca"];

export const handlePieChart = (
    /** @type {{ options: any; series: ApexAxisChartSeries | ApexNonAxisChartSeries; }} */ chartData
) => {
    const options = {
        ...chartData.options,
        dataLabels: {
            enabled: true,
            formatter: function (
                /** @type {any} */ _val,
                /** @type {{ w: { globals: { series: { [x: string]: any; }; }; config: { labels: { [x: string]: any; }; }; }; seriesIndex: string | number; }} */ opts
            ) {
                // get the acual value not the percentage
                const value = opts.w.globals.series[opts.seriesIndex];
                const label = opts.w.config.labels[opts.seriesIndex];
                return `${label}: ${normalizeValue(value)}`;
            },
            offset: -10,
        },
        tooltip: {
            y: {
                formatter: function (/** @type {number} */ val) {
                    return normalizeValue(val);
                },
            },
        },
        legend: {
            show: true,
            position: "bottom",
        },
        colors: colorTheme,
    };

    return (
        <Charts
            options={options}
            series={chartData.series}
            type={"pie"}
            height={350}
            labels={chartData.options.labels}
        />
    );
};

export const handleBarChart = (
    /** @type {{ options: any; series: ApexAxisChartSeries | ApexNonAxisChartSeries; }} */ chartData
) => {
    const options = {
        ...chartData.options,
        plotOptions: {
            bar: {
                horizontal: false,
                columnWidth: "100%",
            },
        },
        fill: {
            opacity: 1,
        },
        stroke: {
            width: 5,
            colors: ["transparent"],
        },
        dataLabels: {
            enabled: true,
            formatter: (/** @type {number} */ val) => normalizeValue(val),
        },
        colors: colorTheme,
        yaxis: {
            labels: {
                formatter: (/** @type {number} */ val) => normalizeValue(val),
            },
        },
    };

    return (
        <Charts
            options={options}
            series={chartData.series === undefined ? [] : chartData.series}
            type="bar"
            height={350}
        />
    );
};

export const handleStackedBarChart = (
    /** @type {{ options: any; series: ApexAxisChartSeries | ApexNonAxisChartSeries; }} */ chartData
) => {
    const options = {
        ...chartData.options,
        chart: {
            ...chartData.options.chart,
            type: "bar",
            stacked: true,
            height: 350,
            stackType: "100%",
            toolbar: {
                show: true,
            },
        },
        tooltip: {
            y: {
                formatter: function (/** @type {number} */ val) {
                    return normalizeValue(val);
                },
            },
        },
        plotOptions: {
            bar: {
                horizontal: true,
                columnWidth: "100%",
            },
        },
        fill: {
            opacity: 1,
        },
        stroke: {
            width: 5,
            colors: ["transparent"],
        },
        legend: {
            position: "bottom",
        },
        colors: colorTheme,
    };
    return (
        <Charts
            options={options}
            series={chartData.series === undefined ? [] : chartData.series}
            type="bar"
            height={350}
        />
    );
};
