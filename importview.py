# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "anywidget==0.9.21",
#     "iiif-anywidget==0.1.0",
#     "marimo>=0.20.2",
#     "traitlets==5.14.3",
# ]
# ///

import marimo

__generated_with = "0.20.2"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _():
    from iiif_anywidget import IIIFViewer

    return (IIIFViewer,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # View images from IIIF manifest in marimo
    """)
    return


@app.cell(hide_code=True)
def _(manifest_url):
    manifest_url
    return


@app.cell(hide_code=True)
def _(mo, selected_canvas_info_url):
    mo.md(f"""
    Viewing `{selected_canvas_info_url}`
    """)
    return


@app.cell(hide_code=True)
def _(mo, thumbnail_gallery, viewer):
    mo.hstack([
        viewer,
        mo.md(""),
        thumbnail_gallery

    ], widths = [75, 5, 20])
    return


@app.cell(hide_code=True)
def _():
    #viewer
    return


@app.cell(hide_code=True)
def _():
    #thumbnail_gallery
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Computation
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ### Display
    """)
    return


@app.cell
def _(mo):
    manifest_url = mo.ui.text(
        value="https://manifests.sub.uni-goettingen.de/iiif/presentation/PPN623133725/manifest",
        full_width=True,
        label="*Enter IIIF manifest URL*:",
    )
    return (manifest_url,)


@app.cell
def _(IIIFViewer, selected_canvas_info_url):
    viewer = IIIFViewer(url=selected_canvas_info_url)
    return (viewer,)


@app.cell
def _(IIIFThumbnailGallery, default_info_url, json, thumbnails):
    thumbnail_gallery = IIIFThumbnailGallery(
        items_json=json.dumps(thumbnails),
        selected_info_url=default_info_url,
    )
    return (thumbnail_gallery,)


@app.cell
def _(thumbnails):
    if thumbnails and isinstance(thumbnails[0], dict):
        default_info_url = (thumbnails[0].get("info_url") or "").strip()
    else:
        default_info_url = ""
    return (default_info_url,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ### Manifest thumbnails
    """)
    return


@app.cell
def _(Path, anywidget, traitlets):
    class IIIFThumbnailGallery(anywidget.AnyWidget):
        _esm = Path(__file__).parent / "iiif_thumbnails.js"
        items_json = traitlets.Unicode("[]").tag(sync=True)
        selected_info_url = traitlets.Unicode("").tag(sync=True)

    return (IIIFThumbnailGallery,)


@app.cell
def _(manifest_url, straight_fetch_json):
    jsonmanifest = straight_fetch_json(manifest_url.value)
    return (jsonmanifest,)


@app.cell
def _(jsonmanifest):
    thumbsdata = extract_thumbnails(jsonmanifest)
    return


@app.cell
def _(thumbnail_gallery):
    selected_canvas_info_url = thumbnail_gallery.selected_info_url.strip()
    return (selected_canvas_info_url,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ### Create HTML display
    """)
    return


@app.cell
def _(html):
    def render_gallery(thumbnails_input):
        cards_local = []
        for gallery_label, gallery_thumb_url in thumbnails_input:
            safe_label_local = html.escape(gallery_label)
            safe_thumb_local = html.escape(gallery_thumb_url)
            cards_local.append(
                f"""
                <div style=\"border: 1px solid var(--gray-4); border-radius: 8px; padding: 8px;\">
                    <img src=\"{safe_thumb_local}\" alt=\"{safe_label_local}\" style=\"width: 100%; height: 120px; object-fit: contain; display: block;\" />
                    <div style=\"font-size: 0.85rem; margin-top: 6px; line-height: 1.25;\">{safe_label_local}</div>
                </div>
                """
            )

        return f"""
        <div style=\"max-height: 520px; overflow-y: auto; padding-right: 4px;\">
            <div style=\"display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 10px;\">
                {''.join(cards_local)}
            </div>
        </div>
        """



    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ### Construct thumbnails from manifest
    """)
    return


@app.cell
def _(jsonmanifest):
    thumbnails = extract_thumbnails(jsonmanifest)
    return (thumbnails,)


@app.function
def thumb_from_service(service):
    if isinstance(service, list) and service:
        service = service[0]
    if not isinstance(service, dict):
        return ""
    base = service.get("@id") or service.get("id")
    if not base:
        return ""
    return f"{base.rstrip('/')}/full/240,/0/default.jpg"


@app.function
def normalize_url(url_value):
    if not isinstance(url_value, str):
        return ""
    clean = url_value.strip()
    if clean.startswith("http://"):
        return "https://" + clean[len("http://") :]
    return clean


@app.function
def thumb_from_thumbnail_field(thumbnail):
    if isinstance(thumbnail, list) and thumbnail:
        thumbnail = thumbnail[0]
    if isinstance(thumbnail, str):
        return normalize_url(thumbnail)
    if isinstance(thumbnail, dict):
        thumb_id = thumbnail.get("id") or thumbnail.get("@id") or ""
        return normalize_url(thumb_id)
    return ""


@app.function
def extract_thumbnails(manifest_input):
    output = []
    if not isinstance(manifest_input, dict):
        return output

    if isinstance(manifest_input.get("items"), list):
        canvases_local = manifest_input.get("items", [])
    elif isinstance(manifest_input.get("sequences"), list) and manifest_input["sequences"]:
        canvases_local = manifest_input["sequences"][0].get("canvases", [])
    else:
        canvases_local = []

    for canvas_index, canvas_item in enumerate(canvases_local, start=1):
        if not isinstance(canvas_item, dict):
            continue

        canvas_label = pick_label(canvas_item.get("label")) or f"Canvas {canvas_index}"
        canvas_thumb_url = thumb_from_thumbnail_field(canvas_item.get("thumbnail"))

        if not canvas_thumb_url:
            if isinstance(canvas_item.get("items"), list) and canvas_item["items"]:
                anno_page_item = canvas_item["items"][0]
                if isinstance(anno_page_item, dict) and isinstance(anno_page_item.get("items"), list) and anno_page_item["items"]:
                    anno_item = anno_page_item["items"][0]
                    if isinstance(anno_item, dict):
                        body_item = anno_item.get("body", {})
                        if isinstance(body_item, dict):
                            canvas_thumb_url = thumb_from_service(body_item.get("service"))
                            if not canvas_thumb_url:
                                body_id = body_item.get("id") or body_item.get("@id") or ""
                                if isinstance(body_id, str) and body_id.strip():
                                    canvas_thumb_url = normalize_url(body_id)

        if not canvas_thumb_url:
            if isinstance(canvas_item.get("images"), list) and canvas_item["images"]:
                image_item = canvas_item["images"][0]
                if isinstance(image_item, dict):
                    resource_item = image_item.get("resource", {})
                    if isinstance(resource_item, dict):
                        canvas_thumb_url = thumb_from_service(resource_item.get("service"))

        canvas_info_url = info_url_from_canvas(canvas_item)

        if canvas_thumb_url:
            output.append(
                {
                    "label": canvas_label,
                    "thumb_url": canvas_thumb_url,
                    "info_url": canvas_info_url,
                }
            )

    return output


@app.function
def info_url_from_service(service):
    if isinstance(service, list) and service:
        service = service[0]
    if not isinstance(service, dict):
        return ""
    base = service.get("@id") or service.get("id")
    if not base:
        return ""
    return f"{base.rstrip('/')}/info.json"


@app.function
def info_url_from_image_id(image_id):
    if not isinstance(image_id, str) or not image_id.strip():
        return ""
    clean = normalize_url(image_id.strip())
    marker = "/full/"
    if marker in clean:
        return normalize_url(f"{clean.split(marker, 1)[0].rstrip('/')}/info.json")
    return ""


@app.function
def info_url_from_canvas(canvas_item):
    if not isinstance(canvas_item, dict):
        return ""

    if isinstance(canvas_item.get("items"), list) and canvas_item["items"]:
        anno_page = canvas_item["items"][0]
        if isinstance(anno_page, dict) and isinstance(anno_page.get("items"), list) and anno_page["items"]:
            anno = anno_page["items"][0]
            if isinstance(anno, dict):
                body = anno.get("body", {})
                if isinstance(body, dict):
                    service_info = info_url_from_service(body.get("service"))
                    if service_info:
                        return service_info
                    body_id = body.get("id") or body.get("@id")
                    derived = info_url_from_image_id(body_id)
                    if derived:
                        return derived

    if isinstance(canvas_item.get("images"), list) and canvas_item["images"]:
        image = canvas_item["images"][0]
        if isinstance(image, dict):
            resource = image.get("resource", {})
            if isinstance(resource, dict):
                service_info = info_url_from_service(resource.get("service"))
                if service_info:
                    return service_info
                resource_id = resource.get("@id") or resource.get("id")
                derived = info_url_from_image_id(resource_id)
                if derived:
                    return derived

    thumbnail = canvas_item.get("thumbnail")
    if isinstance(thumbnail, list) and thumbnail:
        thumbnail = thumbnail[0]
    if isinstance(thumbnail, dict):
        thumb_id = thumbnail.get("id") or thumbnail.get("@id")
        return info_url_from_image_id(thumb_id)
    if isinstance(thumbnail, str):
        return info_url_from_image_id(thumbnail)

    return ""


@app.function
def pick_label(label_value):
    if isinstance(label_value, str):
        return label_value
    if isinstance(label_value, list):
        return str(label_value[0]) if label_value else ""
    if isinstance(label_value, dict):
        if "none" in label_value and isinstance(label_value["none"], list) and label_value["none"]:
            return str(label_value["none"][0])
        for value in label_value.values():
            if isinstance(value, list) and value:
                return str(value[0])
    return ""


@app.cell
def _():
    #if manifest_error:
    #    mo.md(f"⚠️ {manifest_error}")
    #elif not thumbnails:
    #    mo.md("No thumbnails found in this manifest.")
    #else:
    #    mo.Html(_render_gallery(thumbnails))
    return


@app.cell
def _():
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ### Data retrieval
    """)
    return


@app.cell
def _(json, urlopen):
    def straight_fetch_json(url_input: str) -> dict:
        with urlopen(url_input) as response:
            return json.load(response)

    return (straight_fetch_json,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ### Imports
    """)
    return


@app.cell
def _():
    import html
    import json
    from urllib.error import URLError
    from urllib.request import urlopen

    return html, json, urlopen


@app.cell
def _():
    import anywidget
    import traitlets

    return anywidget, traitlets


@app.cell
def _():
    from pathlib import Path

    return (Path,)


if __name__ == "__main__":
    app.run()
