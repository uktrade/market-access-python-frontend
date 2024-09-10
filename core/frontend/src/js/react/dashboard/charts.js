import React from "react";
import Charts from "react-apexcharts";

export const handlePieChart = (/** @type {{ options: ApexCharts.ApexOptions; series: ApexAxisChartSeries | ApexNonAxisChartSeries; }} */ chartData) => {
    return (
        <Charts
            options={chartData.options}
            series={chartData.series}
            type={"pie"}
            height={350}
        />
    );
};

export const handleBarChart = (/** @type {{ options: ApexCharts.ApexOptions; series: ApexAxisChartSeries | ApexNonAxisChartSeries; }} */ chartData) => {
    return (
        <Charts
            options={chartData.options}
            series={chartData.series}
            type="bar"
            height={350}
        />
    );
};

export const handleStackedBarChart = (/** @type {{ options: ApexCharts.ApexOptions; series: ApexAxisChartSeries | ApexNonAxisChartSeries; }} */ chartData) => {
    const options = {
        ...chartData.options,
        plotOptions: {
            bar: {
                horizontal: true,
                columnWidth: '45%',
            },
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
