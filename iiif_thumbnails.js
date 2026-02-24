function parseItems(model) {
    try {
        const raw = model.get("items_json") || "[]";
        const parsed = JSON.parse(raw);
        return Array.isArray(parsed) ? parsed : [];
    } catch {
        return [];
    }
}

function render({ model, el }) {
    const root = document.createElement("div");
    root.style.maxHeight = "520px";
    root.style.overflowY = "auto";
    root.style.paddingRight = "4px";

    const grid = document.createElement("div");
    grid.style.display = "grid";
    grid.style.gridTemplateColumns = "repeat(auto-fill, minmax(150px, 1fr))";
    grid.style.gap = "10px";
    root.appendChild(grid);

    const clearGrid = () => {
        while (grid.firstChild) {
            grid.removeChild(grid.firstChild);
        }
    };

    const draw = () => {
        clearGrid();
        const items = parseItems(model);
        const currentSelected = model.get("selected_info_url") || "";

        for (const item of items) {
            const label = typeof item.label === "string" ? item.label : "Canvas";
            const thumbUrl = typeof item.thumb_url === "string" ? item.thumb_url : "";
            const infoUrl = typeof item.info_url === "string" ? item.info_url : "";

            const card = document.createElement("button");
            card.type = "button";
            card.style.width = "100%";
            card.style.textAlign = "left";
            card.style.border = infoUrl && infoUrl === currentSelected ? "2px solid var(--blue-8)" : "1px solid var(--gray-4)";
            card.style.borderRadius = "8px";
            card.style.padding = "8px";
            card.style.background = "var(--white)";
            card.style.cursor = infoUrl ? "pointer" : "default";

            const img = document.createElement("img");
            img.src = thumbUrl;
            img.alt = label;
            img.style.width = "100%";
            img.style.height = "120px";
            img.style.objectFit = "contain";
            img.style.display = "block";
            card.appendChild(img);

            const caption = document.createElement("div");
            caption.textContent = label;
            caption.style.fontSize = "0.85rem";
            caption.style.marginTop = "6px";
            caption.style.lineHeight = "1.25";
            card.appendChild(caption);

            if (infoUrl) {
                card.addEventListener("click", () => {
                    model.set("selected_info_url", infoUrl);
                    model.save_changes();
                    window.dispatchEvent(
                        new CustomEvent("iiif:select-info-url", {
                            detail: { url: infoUrl },
                        })
                    );
                });
            } else {
                card.disabled = true;
                card.style.opacity = "0.7";
            }

            grid.appendChild(card);
        }
    };

    draw();
    model.on("change:items_json", draw);
    model.on("change:selected_info_url", draw);
    el.appendChild(root);

    return () => {
        model.off("change:items_json", draw);
        model.off("change:selected_info_url", draw);
        root.remove();
    };
}

export default { render };
