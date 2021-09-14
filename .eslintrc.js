module.exports = {
    env: {
        browser: true,
        commonjs: true,
        es2021: true,
        node: true,
    },
    extends: [
        "eslint:recommended",
        "plugin:react/recommended",
        "prettier",
    ],
    parserOptions: {
        ecmaFeatures: {
            jsx: true,
        },
        ecmaVersion: 12,
        sourceType: "module",
    },
    plugins: ["react"],
    ignorePatterns: [
        "core/frontend/dist/**",
        "core/frontent/src/vendor/**"
    ],
    rules: {
        "react/prop-types": "off",
        "no-undef": "off",
        "no-unused-vars": "off",
        "react/no-children-prop": "off",
        "react/jsx-key": "off"
    },
    settings: {
        react: {
            version: "detect",
        },
    },
};
