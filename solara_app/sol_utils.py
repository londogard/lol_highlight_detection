import datetime
from typing import Any, Callable
from solara.components.file_drop import FileInfo
import solara
import polars as pl
import plotly.express as px
from dateutil import parser
from solara_app.folders import CHECKPOINTS, CONVERTED


def persist_uploaded_file(
    filename: str, key: str = "data"
) -> Callable[[FileInfo], None]:
    def func(data: FileInfo) -> None:
        with open(filename, "wb") as f:
            f.write(data[key])

    return func


@solara.component
def ModelFileSelectComponent(
    file: solara.Reactive[str],
    model: solara.Reactive[str],
    clicked: solara.Reactive[bool],
):
    files = [str(p) for p in CONVERTED.glob("*") if p.is_dir()]
    models = [str(p) for p in CHECKPOINTS.rglob("*.ckpt")]
    _clicked = solara.use_reactive(clicked)
    with solara.Card("Select Video/Model"):
        with solara.Columns():
            solara.Select(
                "Select File",
                values=files,
                value=file,
            )
            solara.Select(
                "Select Model",
                values=models,
                value=model,
            )
        solara.Button(
            "Run Inference!",
            color="primary",
            on_click=lambda: _clicked.set(True),
        )


@solara.component
def CutOffChartSelection(
    cut_off: solara.Reactive[int],
    start_stop: solara.Reactive[list[datetime.datetime]],
    df: pl.DataFrame,
):
    div = solara.Column()

    solara.SliderInt(
        "Highlight Y-Cutoff",
        cut_off,
        min=df["preds"].min() + 1,
        max=df["preds"].max(),
        thumb_label="always",
        tick_labels="end_points",
    )
    with div:
        fig = px.line(
            df, x="timestamp", y="preds", line_shape="hv", range_x=start_stop.value
        )
        fig.add_hline(y=cut_off.value, line_color="red")

        def update_vals(relayout_dict: dict[str, Any] | None):
            if relayout_dict is not None:
                layout = relayout_dict["relayout_data"]
                if "xaxis.range[0]" in layout:
                    start_stop.value = [
                        parser.parse(layout["xaxis.range[0]"], ignoretz=True),
                        parser.parse(layout["xaxis.range[1]"], ignoretz=True),
                    ]
                else:
                    xaxis_range = layout["xaxis.range"]
                    start_stop.value = [
                        parser.parse(xaxis_range[0], ignoretz=True),
                        parser.parse(xaxis_range[1], ignoretz=True),
                    ]

        solara.FigurePlotly(fig, on_relayout=update_vals)
