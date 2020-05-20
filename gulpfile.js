'use strict';

const
    gulp = require('gulp'),
    concat = require('gulp-concat'),
    gulpif = require('gulp-if'),
    sass = require('gulp-sass'),
    babel = require('gulp-babel'),
    browserSync = require('browser-sync').create(),
    sourcemaps = require('gulp-sourcemaps'),
    uglify = require('gulp-uglify');


// NOTES
// Useful tips for uglifying - https://stackoverflow.com/questions/24591854/using-gulp-to-concatenate-and-uglify-files


const production = ((process.env.NODE_ENV || 'dev').trim().toLowerCase() === 'prod');

// Source paths
const
    assetsSrcPath = 'core/static/',
    scssEntryFile = assetsSrcPath + 'css/index.scss';

// Build paths
const
    assetsBuildPath = 'core/static/build/',
    cssBuildPath = assetsBuildPath + 'css',
    cssBuildFileName = 'main.css',
    jsBuildPath = assetsBuildPath + 'js';


// BrowserSync Init
const browserSyncInit = () => {
    browserSync.init({
        notify: false,
        open: false,
        proxy: '127.0.0.1:9880',
        port: 9881,
        reloadDelay: 300,
        reloadDebounce: 500,
    });
};


// Prepare Main CSS
const main_css = () => {
    return gulp.src([scssEntryFile])
        .pipe(concat(cssBuildFileName))
        .pipe(gulpif(!production, sourcemaps.init()))
        .pipe(sass({outputStyle: 'compressed'})).on('error', sass.logError)
        .pipe(gulpif(!production, sourcemaps.write('.')))
        .pipe(gulp.dest(cssBuildPath))
        .pipe(browserSync.stream());
};


const main_js = () => {
    return gulp.src([
        'core/static/js/vendor/jessie.js',
        'core/static/js/vendor/body-scroll-lock.js',
        'core/static/js/datahub-header/component/header.js',
        'core/static/js/ma.js',
        'core/static/js/ma.CustomEvent.js',
        'core/static/js/ma.xhr2.js',
        'core/static/js/components/ConditionalRadioContent.js',
        'core/static/js/components/FileUpload.js',
        'core/static/js/components/Collapsible.js',
        'core/static/js/components/TextArea.js',
        'core/static/js/components/ToggleLinks.js',
        'core/static/js/components/Toast.js',
        'core/static/js/components/CharacterCount.js',
        'core/static/js/components/Attachments.js',
        'core/static/js/components/Modal.js',
        'core/static/js/components/DeleteModal.js',
        'core/static/js/components/ToggleBox.js',
        'core/static/js/components/AttachmentForm.js',
        'core/static/js/pages/index.js',
        'core/static/js/pages/report/index.js',
        'core/static/js/pages/report/is-resolved.js',
        'core/static/js/pages/report/about-problem.js',
        'core/static/js/pages/barrier/status.js',
        'core/static/js/pages/barrier/type.js',
        'core/static/js/pages/barrier/edit.js',
        'core/static/js/pages/barrier/detail.js',
        'core/static/js/pages/barrier/team.js',
        'core/static/js/pages/barrier/assessment.js',
        'core/static/js/pages/barrier/archive.js',
        'core/static/js/pages/barrier/wto.js',
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
                preamble: "/* Licensing info */"
            }
        }))
        .pipe(concat('main.js'))
        .pipe(gulpif(!production, sourcemaps.write('.')))
        .pipe(gulp.dest(jsBuildPath))
        .pipe(browserSync.stream());
};

const watchFiles = () => {
    browserSyncInit();
    // gulp.watch('**/*.html').on('change', () => browserSync.reload());
    gulp.watch('robo/static/scss/**/*.scss').on('change', () => {
        main_css();
        browserSync.reload();
    });
    gulp.watch('robo/static/js/**/*.js').on('change', () => {
        main_js();
        browserSync.reload();
    });

};

const watchCss = () => {
    gulp.watch('robo/static/scss/**/*.scss').on('change', () => {
        main_css();
    });
};

const watch = watchFiles;
const watchcss = watchCss;
const css = main_css;
const js = main_js;
const build = gulp.parallel(css, js);
const fe = gulp.series(build, watch);

// Export Commands
exports.css = css;
exports.js = js;
exports.watch = watch;
exports.watchcss = watchcss;
exports.build = build;
exports.fe = fe;

exports.default = fe;
