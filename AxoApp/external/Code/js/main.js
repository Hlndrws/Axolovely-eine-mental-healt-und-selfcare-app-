// Das bestehende Skript für das wechselnde Logo...
document.addEventListener('DOMContentLoaded', function() {
    const bild = document.getElementById('meinBild');
    if (bild) {
        bild.addEventListener('click', function(event) {
            event.preventDefault();
            const aktuellesSrc = bild.src;
            const alternativesSrc = bild.getAttribute('data-alt-src');
            bild.src = alternativesSrc;
            bild.setAttribute('data-alt-src', aktuellesSrc);
        });
    }
});

// NEU: Globaler Klick-Handler für schließbare Alert-Meldungen
document.addEventListener("click", (event) => {
    const closeButton = event.target.closest("[data-dismiss-message]");
    if (closeButton) {
        closeButton.closest(".alert").remove();
    }
});
