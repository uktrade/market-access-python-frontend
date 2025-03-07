const path = require("path");
const BundleTracker = require("webpack-bundle-tracker");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const WebpackConcatPlugin = require("webpack-concat-files-plugin");
const CopyPlugin = require("copy-webpack-plugin");
const babel = require("@babel/core");

const assetsSrcPath = path.resolve(__dirname, "core/frontend/src/");

const mainConfig = {
    entry: {
        style: path.resolve(__dirname, "core/frontend/src/css/index.scss"),
        date_filter_component: path.resolve(
            __dirname,
            "core/frontend/src/js/components/resolved_date_filter.js"
        ),
        csv_download_result_component: path.resolve(
            __dirname,
            "core/frontend/src/js/components/download_csv.js"
        ),
    },
    output: {
        path: path.resolve(__dirname, "./core/frontend/dist/webpack_bundles"),
        publicPath: "/static/webpack_bundles/",
        filename: "[name]-[fullhash].js",
        clean: true,
        iife: false,
    },
    plugins: [
        new BundleTracker({ filename: "./webpack-stats.json" }),
        new MiniCssExtractPlugin({
            filename: "[name]-[fullhash].css",
            chunkFilename: "[id]-[fullhash].css",
        }),
        new CopyPlugin({
            patterns: [
                {
                    from: path.resolve(
                        __dirname,
                        "./core/frontend/src/images/"
                    ),
                    to: "../images",
                },
            ],
        }),
        // we need to unfonruntately bundle all the js files sequentially as there's no main entry point
        // the entry point gets generated and used by the babel-loader defined below
        new WebpackConcatPlugin({
            bundles: [
                {
                    dest: path.resolve(
                        __dirname,
                        "./core/frontend/dist/webpack_bundles/main.js"
                    ),
                    transforms: {
                        after: async (code) => {
                            const transcompiledFile = await babel.transform(
                                code,
                                {
                                    presets: [
                                        ["@babel/env", { modules: false }],
                                    ],
                                }
                            );
                            return transcompiledFile.code;
                        },
                    },
                    src: [
                        `${assetsSrcPath}/js/vendor/jessie.js`,
                        `${assetsSrcPath}/js/vendor/body-scroll-lock.js`,
                        `${assetsSrcPath}/js/datahub-header/component/header.js`,
                        `${assetsSrcPath}/js/ma.js`,
                        `${assetsSrcPath}/js/ma.CustomEvent.js`,
                        `${assetsSrcPath}/js/ma.xhr2.js`,
                        `${assetsSrcPath}/js/components/ConditionalRadioContent.js`,
                        `${assetsSrcPath}/js/components/FileUpload.js`,
                        `${assetsSrcPath}/js/components/Collapsible.js`,
                        `${assetsSrcPath}/js/components/TextArea.js`,
                        `${assetsSrcPath}/js/components/Toast.js`,
                        `${assetsSrcPath}/js/components/CharacterCount.js`,
                        `${assetsSrcPath}/js/components/Attachments.js`,
                        `${assetsSrcPath}/js/components/Modal.js`,
                        `${assetsSrcPath}/js/components/DeleteModal.js`,
                        `${assetsSrcPath}/js/components/AttachmentForm.js`,
                        `${assetsSrcPath}/js/components/HiddenEstimatedResolutionDateTextarea.js`,
                        `${assetsSrcPath}/js/components/HiddenRadioContent.js`,
                        `${assetsSrcPath}/js/components/MultiSelect.js`,
                        `${assetsSrcPath}/js/pages/index.js`,
                        `${assetsSrcPath}/js/pages/report/location-wizard-step.js`,
                        `${assetsSrcPath}/js/pages/report/sectors-wizard-step.js`,
                        `${assetsSrcPath}/js/pages/report/status-wizard-step.js`,
                        `${assetsSrcPath}/js/pages/barrier/status.js`,
                        `${assetsSrcPath}/js/pages/barrier/edit.js`,
                        `${assetsSrcPath}/js/pages/barrier/priority.js`,
                        `${assetsSrcPath}/js/pages/barrier/top_barrier_priority.js`,
                        `${assetsSrcPath}/js/pages/barrier/detail.js`,
                        `${assetsSrcPath}/js/pages/barrier/team.js`,
                        `${assetsSrcPath}/js/pages/barrier/assessment.js`,
                        `${assetsSrcPath}/js/pages/barrier/archive.js`,
                        `${assetsSrcPath}/js/pages/barrier/wto.js`,
                        `${assetsSrcPath}/js/pages/barrier/action_plans_add_task.js`,
                        `${assetsSrcPath}/js/pages/users/select.js`,
                    ],
                },
            ],
            allowOptimization: true,
        }),
    ],
    module: {
        rules: [
            {
                test: /\.(woff2?)$/i,
                type: "asset/resource",
                generator: {
                    filename: "../fonts/[name].[ext]",
                },
            },
            {
                test: /\.(png|jpe?g|gif|svg|ico|eot)$/i,
                type: "asset/resource",
                generator: {
                    filename: "../images/[name].[ext]",
                },
            },
            {
                test: /\.s[ac]ss$/i,
                use: [
                    {
                        loader: MiniCssExtractPlugin.loader,
                    },
                    "css-loader",
                    "sass-loader",
                ],
            },
        ],
    },

    resolve: {
        modules: ["node_modules"],
        extensions: [".js", ".scss", ".ts"],
    },

    devtool: "source-map",
};

// React components need special configuration

const reactConfig = {
    entry: path.resolve(__dirname, "core/frontend/src/js/react"),
    output: {
        path: path.resolve(__dirname, "core/frontend/dist/webpack_bundles/"),
        filename: "react_deployed.js",
        libraryTarget: "var",
        library: "ReactApp",
    },
    resolve: {
        extensions: [".js", ".jsx", ".ts", ".tsx"],
    },
    plugins: [new BundleTracker({ filename: "./webpack-stats-react.json" })],
    module: {
        rules: [
            {
                test: /\.(js|jsx|ts|tsx)$/,
                exclude: /node_modules/,
                use: {
                    loader: "babel-loader",
                    options: {
                        presets: [
                            "@babel/react",
                            "@babel/typescript",
                            ["@babel/env", { modules: false }],
                        ],
                        plugins: ["@babel/plugin-transform-runtime"],
                    },
                },
            },
            {
                test: /\.s[ac]ss$/i,
                use: [
                    {
                        loader: MiniCssExtractPlugin.loader,
                    },
                    "css-loader",
                    "sass-loader",
                ],
            },
        ],
    },
    devtool: "source-map",
};

module.exports = [mainConfig, reactConfig];
