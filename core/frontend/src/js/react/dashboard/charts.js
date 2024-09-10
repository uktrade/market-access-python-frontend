import React from "react";
import Charts from "react-apexcharts";

export const handlePieChart = (
    /** @type {{ options: any; series: ApexAxisChartSeries | ApexNonAxisChartSeries; }} */ chartData,
) => {
    const options = {
        ...chartData.options,
        dataLabels: {
            enabled: true,
            formatter: function (val, opts) {
                // get the acual value not the percentage
                const value = opts.w.globals.series[opts.seriesIndex];
                const label = opts.w.config.labels[opts.seriesIndex];
                return `${label}: ${value}`;
            },
            offset: -10,
        },
        legend: {
            show: false,
        },
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
    /** @type {{ options: any; series: ApexAxisChartSeries | ApexNonAxisChartSeries; }} */ chartData,
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
        },
    };
    return (
        <Charts
            options={options}
            series={chartData.series}
            type="bar"
            height={350}
        />
    );
};

export const handleStackedBarChart = (
    /** @type {{ options: any; series: ApexAxisChartSeries | ApexNonAxisChartSeries; }} */ chartData,
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
        dataLabels: {
            enabled: true,
        },
        legend: {
            position: "bottom",
        },
    };
    return (
        <Charts
            options={options}
            series={chartData.series}
            type="bar"
            height={350}
        />
    );
};
