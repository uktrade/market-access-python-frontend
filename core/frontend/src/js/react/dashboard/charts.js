import React from "react";
import Charts from "react-apexcharts";

export const handlePieChart = (chartData) => {
    return (
        <Charts
            options={chartData.options}
            series={chartData.series}
            type={"pie"}
            height={350}
        />
    );
};

export const handleBarChart = (chartData) => {
    return (
        <Charts
            options={chartData.options}
            series={chartData.series}
            type="bar"
            height={350}
        />
    );
};

export const handleStackedBarChart = (chartData) => {
    return (
        <Charts
            options={chartData.options}
            series={chartData.series}
            type="bar"
            height={350}
        />
    );
};
