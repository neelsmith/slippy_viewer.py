import marimo

__generated_with = "0.19.6"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return


@app.cell
def _():
    from pathlib import Path
    return (Path,)


@app.cell
def _(Path):
    import anywidget
    import traitlets

    class IIIFViewer(anywidget.AnyWidget):
        _esm = Path(__file__).parent / "iiif_viewer.js"
        url = traitlets.Unicode().tag(sync=True)
    return (IIIFViewer,)


@app.cell
def _(IIIFViewer):
    viewer = IIIFViewer(url="https://framemark.vam.ac.uk/collections/2006AN7529/info.json")
    return (viewer,)


@app.cell
def _(viewer):
    viewer
    return


if __name__ == "__main__":
    app.run()
