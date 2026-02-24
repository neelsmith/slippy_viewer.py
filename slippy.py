import marimo

__generated_with = "0.20.2"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # IIIF Viewer in marimo
    """)
    return


@app.cell
def _(IIIFViewer):
    viewer = IIIFViewer(url="https://framemark.vam.ac.uk/collections/2006AN7529/info.json")
    return (viewer,)


@app.cell
def _(viewer):
    viewer
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Computation
    """)
    return


@app.cell
def _():
    from pathlib import Path

    return (Path,)


@app.cell
def _():
    import anywidget
    import traitlets

    return anywidget, traitlets


@app.cell
def _(Path, anywidget, traitlets):
    class IIIFViewer(anywidget.AnyWidget):
        _esm = Path(__file__).parent / "iiif_viewer.js"
        url = traitlets.Unicode().tag(sync=True)

    return (IIIFViewer,)


if __name__ == "__main__":
    app.run()
