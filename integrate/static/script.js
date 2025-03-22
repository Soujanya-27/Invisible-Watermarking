document.addEventListener("DOMContentLoaded", function() {
    // Simulated loader
    setTimeout(function() {
        document.getElementById("loader").style.display = "none";
        document.getElementById("selection").style.display = "block";
    }, 2000);

    // Handle browser back/forward buttons
    window.onpopstate = function(event) {
        if (event.state) {
            showPage(event.state.page, false);
        }
    };

    // If page is loaded with a hash (e.g., #embedPage), show it
    if (location.hash) {
        const page = location.hash.substring(1);
        if (["embedPage", "extractPage"].includes(page)) {
            showPage(page, false);
        }
    }
});

function showEmbedPage() {
    document.getElementById("selection").style.display = "none";
    document.getElementById("embedPage").style.display = "block";
    document.getElementById("extractPage").style.display = "none";
    history.pushState({ page: "embedPage" }, "", "#embedPage");
}

function showExtractPage() {
    document.getElementById("selection").style.display = "none";
    document.getElementById("extractPage").style.display = "block";
    document.getElementById("embedPage").style.display = "none";
    history.pushState({ page: "extractPage" }, "", "#extractPage");
}

function goBack() {
    document.getElementById("embedPage").style.display = "none";
    document.getElementById("extractPage").style.display = "none";
    document.getElementById("selection").style.display = "block";
    history.pushState({ page: "selection" }, "", "#selection");
}

function showPage(pageId, pushState = true) {
    // Hide all sections
    document.getElementById("selection").style.display = "none";
    document.getElementById("embedPage").style.display = "none";
    document.getElementById("extractPage").style.display = "none";

    // Show the requested section
    document.getElementById(pageId).style.display = "block";

    // Update browser history
    if (pushState) {
        history.pushState({ page: pageId }, "", `#${pageId}`);
    }
}