const path = require('path');

module.exports = {
    entry: path.resolve(__dirname, 'core/frontend/src/js/react'),
    output: {
        path: path.resolve(__dirname, 'core/frontend/dist/js/'),
        filename: 'react.js',
        libraryTarget: 'var',
        library: 'ReactApp'
    },
    devtool: "sourcemap",
    module: {
        rules: [{
            test: /\.js$/,
            exclude: /node_modules/,
            use: {
              loader: 'babel-loader',
              options: {
                presets: ["@babel/preset-react", '@babel/preset-env']
              }
            }
        }]
   }
};
