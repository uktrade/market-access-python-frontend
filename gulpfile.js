'use strict';

const production = ((process.env.NODE_ENV || 'dev').trim().toLowerCase() === 'production');
const
    gulp = require('gulp'),
    concat = require('gulp-concat'),
    gulpif = require('gulp-if'),
    babel = require('gulp-babel'),
    sourcemaps = require('gulp-sourcemaps'),
    uglify = require('gulp-uglify'),
    webpack = require('webpack-stream');

const sass = require('gulp-sass')(require('sass'));

// NOTES
// Useful tips for uglifying - https://stackoverflow.com/questions/24591854/using-gulp-to-concatenate-and-uglify-files

// Source paths
const
    assetsSrcPath = 'core/frontend/src/',
    scssEntryFile = `${assetsSrcPath}css/index.scss`,
    govukAssets = 'node_modules/govuk-frontend/govuk/assets/';

// Build / Distribution paths
const
    assetsBuildPath = 'core/frontend/dist/',
    cssBuildPath = `${assetsBuildPath}css`,
    cssBuildFileName = 'main.css',
    jsBuildPath = `${assetsBuildPath}js`,
    jsBuildFileName = 'main.js';

const
    jsLicensingInfo = '/* Licensing info */';

// Prepare Main CSS
const main_css = () => {
    return gulp.src([scssEntryFile])
        .pipe(concat(cssBuildFileName))
        .pipe(gulpif(!production, sourcemaps.init()))
        .pipe(sass({outputStyle: 'compressed'})).on('error', sass.logError)
        .pipe(gulpif(!production, sourcemaps.write('.')))
        .pipe(gulp.dest(cssBuildPath));
};

// Prepare Main JS
const main_js = () => {
    return gulp.src([
        `${assetsSrcPath}js/vendor/jessie.js`,
        `${assetsSrcPath}js/vendor/body-scroll-lock.js`,
        `${assetsSrcPath}js/datahub-header/component/header.js`,
        `${assetsSrcPath}js/ma.js`,
        `${assetsSrcPath}js/ma.CustomEvent.js`,
        `${assetsSrcPath}js/ma.xhr2.js`,
        `${assetsSrcPath}js/components/ConditionalRadioContent.js`,
        `${assetsSrcPath}js/components/FileUpload.js`,
        `${assetsSrcPath}js/components/Collapsible.js`,
        `${assetsSrcPath}js/components/TextArea.js`,
        `${assetsSrcPath}js/components/ToggleLinks.js`,
        `${assetsSrcPath}js/components/Toast.js`,
        `${assetsSrcPath}js/components/CharacterCount.js`,
        `${assetsSrcPath}js/components/Attachments.js`,
        `${assetsSrcPath}js/components/Modal.js`,
        `${assetsSrcPath}js/components/DeleteModal.js`,
        `${assetsSrcPath}js/components/ToggleBox.js`,
        `${assetsSrcPath}js/components/AttachmentForm.js`,
        `${assetsSrcPath}js/pages/index.js`,
        `${assetsSrcPath}js/pages/report/index.js`,
        `${assetsSrcPath}js/pages/report/is-resolved.js`,
        `${assetsSrcPath}js/pages/report/about-problem.js`,
        `${assetsSrcPath}js/pages/barrier/status.js`,
        `${assetsSrcPath}js/pages/barrier/type.js`,
        `${assetsSrcPath}js/pages/barrier/edit.js`,
        `${assetsSrcPath}js/pages/barrier/detail.js`,
        `${assetsSrcPath}js/pages/barrier/team.js`,
        `${assetsSrcPath}js/pages/barrier/assessment.js`,
        `${assetsSrcPath}js/pages/barrier/archive.js`,
        `${assetsSrcPath}js/pages/barrier/wto.js`,
        `${assetsSrcPath}js/pages/barrier/action_plans_add_task.js`,
    ])
        .pipe(gulpif(!production, sourcemaps.init()))
        .pipe(babel({
            presets: [
                ['@babel/env', {
                    modules: false
                }]
            ]
        }))
        .pipe(uglify({
            // https://github.com/mishoo/UglifyJS#mangle-options
            mangle: {
                toplevel: false
            },
            // https://github.com/mishoo/UglifyJS#compress-options
            compress: {
                drop_console: production
            },
            // https://github.com/mishoo/UglifyJS#output-options
            output: {
                beautify: !production,
                preamble: jsLicensingInfo
            }
        }))
        .pipe(concat(jsBuildFileName))
        .pipe(gulpif(!production, sourcemaps.write('.')))
        .pipe(gulp.dest(jsBuildPath));
};

// Prepare React
const main_react = () => {
    return gulp.src("js/react/*")
        .pipe(webpack(require('./webpack.config.js')))
        .pipe(gulp.dest(jsBuildPath));
};


// Move files to dist
const copyFonts = () => {
    return gulp.src(`${govukAssets}fonts/*`)
        .pipe(gulp.dest('core/static/govuk-public/fonts'));
};


// BrowserSync Init
const browserSyncInit = (browserSync) => {
    browserSync.init({
        notify: false,
        open: false,
        proxy: '127.0.0.1:9880',
        port: 9881,
        reloadDelay: 300,
        reloadDebounce: 500,
    });
};

// File watchers
const watchFiles = () => {
    const browserSync = require('browser-sync').create();
    browserSyncInit(browserSync);
    // gulp.watch('**/*.html').on('change', () => browserSync.reload());
    gulp.watch(`${assetsSrcPath}css/**/*.scss`).on('change', () => {
        main_css().pipe(browserSync.stream());
        browserSync.reload();
    });
    gulp.watch(`${assetsSrcPath}js/**/*.js`).on('change', () => {
        main_js().pipe(browserSync.stream());
        browserSync.reload();
    });
    gulp.watch(`${assetsSrcPath}js/react/**/*.js`).on('change', () => {
        main_react().pipe(browserSync.stream());
        browserSync.reload();
    });
};

const watchCss = () => {
    gulp.watch(`${assetsSrcPath}css/**/*.scss`).on('change', () => {
        main_css();
    });
};

// Command definitions
const watch = watchFiles;
const watchcss = watchCss;
const css = main_css;
const js = main_js;
const react = main_react;
const build = gulp.parallel(css, js, react, copyFonts);
const fe = gulp.series(build, watch);

// Export Commands
exports.css = css;
exports.js = js;
exports.react = react;
exports.watch = watch;
exports.watchcss = watchcss;
exports.build = build;
exports.fe = fe;

exports.default = fe;
