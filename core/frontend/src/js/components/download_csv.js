const download_csv_results_box = document.getElementById(
    "download-csv-confirmation"
);

const filter_results_list = document.getElementById("filter-results-list");

if (download_csv_results_box) {
    var csvResultBox = document.getElementById("download-csv-confirmation");
    var barrierListBox = document.getElementById("filter-results-list");

    setTimeout(fadeResultBox, 1000);

    csvResultBox.addEventListener("webkitAnimationEnd", removeResultBox);
    csvResultBox.addEventListener("animationend", removeResultBox);
}

function fadeResultBox() {
    // Get the height of the csv-result-box and pass that as a parameter
    // to determine how far the barrier list has to raise during its animation
    var resultBoxHeight = parseInt(csvResultBox.offsetHeight);

    barrierListBox.style.setProperty(
        "--csv-box-height",
        "-" + resultBoxHeight + "px"
    );

    csvResultBox.classList.add("csv-box-animate");
    barrierListBox.classList.add("csv-box-barrier-list-animate");
}

function removeResultBox() {
    // Removing box outright makes the barrier list jump,
    // so move the now invisible box behind all the elements
    csvResultBox.classList.add("csv-box-post-animation-state");
}
