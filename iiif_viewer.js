function loadOpenSeadragon() {
    if (window.OpenSeadragon) {
        return Promise.resolve(window.OpenSeadragon);
    }

    return new Promise((resolve, reject) => {
        const existing = document.querySelector('script[data-osd="1"]');
        if (existing) {
            existing.addEventListener("load", () => resolve(window.OpenSeadragon), { once: true });
            existing.addEventListener("error", () => reject(new Error("Failed to load OpenSeadragon")), { once: true });
            return;
        }

        const script = document.createElement("script");
        script.src = "https://cdn.jsdelivr.net/npm/openseadragon@5.0.0/build/openseadragon/openseadragon.min.js";
        script.dataset.osd = "1";
        script.onload = () => resolve(window.OpenSeadragon);
        script.onerror = () => reject(new Error("Failed to load OpenSeadragon"));
        document.head.appendChild(script);
    });
}

function render({ model, el }) {
    const container = document.createElement("div");
    container.style.width = "100%";
    container.style.height = "500px";
    el.appendChild(container);

    let viewer;
    let stopListening = () => {};
    let stopGlobalSelectionListening = () => {};

    loadOpenSeadragon().then((OpenSeadragon) => {
        viewer = OpenSeadragon({
            element: container,
            prefixUrl: "https://cdn.jsdelivr.net/npm/openseadragon@5.0.0/build/openseadragon/images/",
        });

        const openFromModel = () => {
            const url = model.get("url");
            if (url) {
                viewer.open(url);
            }
        };

        openFromModel();
        model.on("change:url", openFromModel);
        stopListening = () => model.off("change:url", openFromModel);

        const openFromThumbnailSelection = (event) => {
            const selectedUrl = event?.detail?.url;
            if (!selectedUrl) {
                return;
            }

            model.set("url", selectedUrl);
            model.save_changes();
            viewer.open(selectedUrl);
        };

        window.addEventListener("iiif:select-info-url", openFromThumbnailSelection);
        stopGlobalSelectionListening = () => {
            window.removeEventListener("iiif:select-info-url", openFromThumbnailSelection);
        };
    });

    return () => {
        stopListening();
        stopGlobalSelectionListening();
        if (viewer) {
            viewer.destroy();
        }
        container.remove();
    };
}

export default { render };