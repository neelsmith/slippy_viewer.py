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

    const status = document.createElement("div");
    status.style.fontSize = "0.8rem";
    status.style.color = "var(--gray-8)";
    status.style.marginBottom = "8px";
    status.textContent = "Loading thumbnails...";
    root.appendChild(status);

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

    const supportsIntersectionObserver = typeof window !== "undefined" && "IntersectionObserver" in window;
    const lazyImageObserver = supportsIntersectionObserver
        ? new IntersectionObserver(
              (entries) => {
                  for (const entry of entries) {
                      if (!entry.isIntersecting) {
                          continue;
                      }

                      const img = entry.target;
                      const deferredSrc = img.dataset.deferredSrc;
                      if (deferredSrc && img.src !== deferredSrc) {
                          img.src = deferredSrc;
                      }
                      lazyImageObserver.unobserve(img);
                  }
              },
              {
                  root,
                  rootMargin: "300px 0px",
              }
          )
        : null;

    let drawToken = 0;
    let pendingFrame = null;

    const buildCard = (item, currentSelected, onThumbSettled) => {
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
        img.alt = label;
        img.style.width = "100%";
        img.style.height = "120px";
        img.style.objectFit = "contain";
        img.style.display = "block";
        img.loading = "lazy";
        img.decoding = "async";

        let settled = false;
        const settleThumb = () => {
            if (settled) {
                return;
            }
            settled = true;
            onThumbSettled();
        };

        if (thumbUrl) {
            img.addEventListener("load", settleThumb, { once: true });
            img.addEventListener("error", settleThumb, { once: true });
            if (lazyImageObserver) {
                img.dataset.deferredSrc = thumbUrl;
                lazyImageObserver.observe(img);
            } else {
                img.src = thumbUrl;
            }
        } else {
            settleThumb();
        }

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

        return card;
    };

    const draw = () => {
        drawToken += 1;
        const currentToken = drawToken;
        if (pendingFrame !== null) {
            cancelAnimationFrame(pendingFrame);
            pendingFrame = null;
        }

        clearGrid();
        if (lazyImageObserver) {
            lazyImageObserver.disconnect();
        }
        const items = parseItems(model);
        const currentSelected = model.get("selected_info_url") || "";
        const total = items.length;
        let loaded = 0;

        const updateStatus = () => {
            if (!total) {
                status.textContent = "No thumbnails found.";
                return;
            }
            if (loaded < total) {
                status.textContent = `Loading thumbnails ${loaded} / ${total}`;
                return;
            }
            status.textContent = `Loaded ${total} thumbnails`;
        };

        const markThumbSettled = () => {
            if (currentToken !== drawToken) {
                return;
            }
            loaded += 1;
            updateStatus();
        };

        updateStatus();
        let cursor = 0;
        const chunkSize = 30;

        const appendChunk = () => {
            if (currentToken !== drawToken) {
                return;
            }

            const fragment = document.createDocumentFragment();
            const upperBound = Math.min(cursor + chunkSize, items.length);

            for (; cursor < upperBound; cursor += 1) {
                fragment.appendChild(buildCard(items[cursor], currentSelected, markThumbSettled));
            }

            grid.appendChild(fragment);

            if (cursor < items.length) {
                pendingFrame = requestAnimationFrame(appendChunk);
            } else {
                pendingFrame = null;
            }
        };

        pendingFrame = requestAnimationFrame(appendChunk);
    };

    draw();
    model.on("change:items_json", draw);
    model.on("change:selected_info_url", draw);
    el.appendChild(root);

    return () => {
        drawToken += 1;
        if (pendingFrame !== null) {
            cancelAnimationFrame(pendingFrame);
            pendingFrame = null;
        }
        if (lazyImageObserver) {
            lazyImageObserver.disconnect();
        }
        model.off("change:items_json", draw);
        model.off("change:selected_info_url", draw);
        root.remove();
    };
}

export default { render };
