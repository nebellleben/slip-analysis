import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from typing import Dict, List, Optional
from datetime import date

from utils.data_processor import get_date_normalized


def _add_rainfall_background(
    fig: go.Figure,
    df: pd.DataFrame,
    rainfall_data: Optional[pd.DataFrame],
    show_rainfall: bool = True,
) -> None:
    if not show_rainfall:
        return
    if rainfall_data is None or rainfall_data.empty:
        return

    if df.empty:
        return

    unique_dates = sorted(df["Date"].unique())
    if len(unique_dates) == 0:
        return
    if len(unique_dates) == 1:
        return

    max_rainfall = rainfall_data["Rainfall"].max()
    if max_rainfall == 0:
        max_rainfall = 1

    for i, dt in enumerate(unique_dates):
        if isinstance(dt, date):
            dt_date = dt
        else:
            dt_date = pd.to_datetime(dt).date()

        rain_row = rainfall_data[rainfall_data["Date"].dt.date == dt_date]
        if len(rain_row) > 0:
            rainfall = rain_row["Rainfall"].values[0]
        else:
            rainfall = 0

        if rainfall > 0:
            alpha = min(0.75, rainfall / max_rainfall * 0.70 + 0.08)
        else:
            alpha = 0.03

        if i < len(unique_dates) - 1:
            next_dt = unique_dates[i + 1]
            y1 = str(next_dt)
        else:
            y1 = str(dt)

        fig.add_shape(
            type="rect",
            xref="paper",
            yref="y",
            x0=0,
            y0=str(dt),
            x1=1,
            y1=y1,
            fillcolor=f"rgba(25, 55, 140, {alpha})",
            layer="below",
            line=dict(width=0),
        )

    n_ticks = 5
    tick_vals = [i / (n_ticks - 1) for i in range(n_ticks)]
    tick_labels = [f"{int(v * max_rainfall)}" for v in tick_vals]

    fig.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            marker=dict(
                colorscale=[
                    [0, "rgba(25, 55, 140, 0.03)"],
                    [1, "rgba(25, 55, 140, 0.75)"],
                ],
                cmin=0,
                cmax=max_rainfall,
                colorbar=dict(
                    title="Rainfall (mm)",
                    tickvals=[v * max_rainfall for v in tick_vals],
                    ticktext=tick_labels,
                    len=0.6,
                    y=0.5,
                    yanchor="middle",
                    outlinewidth=0,
                ),
                showscale=True,
            ),
            hoverinfo="none",
            showlegend=False,
        )
    )


def create_date_location_scatter(
    df: pd.DataFrame,
    location_order: Dict[str, int],
    title: str = "Slip Occurrences: Date vs Location",
    selected_trains: Optional[List[str]] = None,
    rainfall_data: Optional[pd.DataFrame] = None,
    show_rainfall: bool = True,
) -> go.Figure:
    if df.empty:
        return go.Figure()

    df = df.copy()

    if selected_trains:
        df = df[df["Display_ID"].isin(selected_trains)]

    df["Location_Order"] = df["Position"].map(location_order)
    df = df.dropna(subset=["Location_Order"])
    df = df.sort_values("Location_Order")

    occurrence_counts = (
        df.groupby(["Date", "Position"]).size().reset_index(name="Count")
    )
    occurrence_counts["Location_Order"] = occurrence_counts["Position"].map(
        location_order
    )
    occurrence_counts = occurrence_counts.sort_values("Location_Order")

    fig = px.scatter(
        occurrence_counts,
        x="Position",
        y="Date",
        size="Count",
        title=title,
        labels={"Position": "Location", "Date": "Date", "Count": "Occurrences"},
        category_orders={
            "Position": [
                k for k, v in sorted(location_order.items(), key=lambda x: x[1])
            ]
        },
    )

    _add_rainfall_background(fig, occurrence_counts, rainfall_data, show_rainfall)

    fig.update_layout(
        xaxis_tickangle=-45,
        height=500,
        xaxis_title="Location (Sequential Order)",
        yaxis_title="Date",
    )

    return fig


def create_date_train_scatter(
    df: pd.DataFrame,
    title: str = "Slip Occurrences: Date vs Train",
    selected_trains: Optional[List[str]] = None,
    rainfall_data: Optional[pd.DataFrame] = None,
    show_rainfall: bool = True,
) -> go.Figure:
    if df.empty:
        return go.Figure()

    df = df.copy()

    if selected_trains:
        df = df[df["Display_ID"].isin(selected_trains)]

    occurrence_counts = (
        df.groupby(["Date", "Display_ID"]).size().reset_index(name="Count")
    )

    train_order = sorted(
        occurrence_counts["Display_ID"].unique(),
        key=lambda x: (len(str(x)), str(x)),
    )

    fig = px.scatter(
        occurrence_counts,
        x="Display_ID",
        y="Date",
        size="Count",
        size_max=30,
        hover_name="Display_ID",
        hover_data={"Display_ID": True, "Date": True, "Count": True},
        title=title,
        labels={"Display_ID": "Train ID", "Date": "Date", "Count": "Occurrences"},
        category_orders={"Display_ID": train_order},
    )

    _add_rainfall_background(fig, occurrence_counts, rainfall_data, show_rainfall)

    fig.update_traces(
        marker=dict(
            sizemin=8,
            line=dict(width=1, color="white"),
        )
    )

    fig.update_layout(
        xaxis_tickangle=-45,
        height=500,
        xaxis_title="Train ID",
        yaxis_title="Date",
    )

    return fig


def create_train_location_scatter(
    df: pd.DataFrame,
    location_order: Dict[str, int],
    title: str = "Slip Occurrences: Train vs Location",
    sort_by_frequency: bool = False,
) -> go.Figure:
    if df.empty:
        return go.Figure()

    df = df.copy()
    df = get_date_normalized(df)
    df["Date_Numeric_Reversed"] = 1 - df["Date_Numeric"]
    df["Location_Order"] = df["Position"].map(location_order)
    df = df.dropna(subset=["Location_Order"])

    occurrence_counts = (
        df.groupby(["Date", "Display_ID", "Position", "Date_Numeric_Reversed"])
        .size()
        .reset_index(name="Count")
    )
    occurrence_counts["Location_Order"] = occurrence_counts["Position"].map(
        location_order
    )

    if sort_by_frequency:
        train_counts = (
            occurrence_counts.groupby("Display_ID")["Count"]
            .sum()
            .sort_values(ascending=True)
        )
        train_order = train_counts.index.tolist()
    else:
        train_order = sorted(
            occurrence_counts["Display_ID"].unique(),
            key=lambda x: (len(str(x)), str(x)),
        )

    unique_dates = sorted(occurrence_counts["Date"].unique())

    fig = px.scatter(
        occurrence_counts,
        x="Position",
        y="Display_ID",
        color="Date_Numeric_Reversed",
        size="Count",
        size_max=30,
        hover_name="Display_ID",
        hover_data={
            "Display_ID": True,
            "Position": True,
            "Date": True,
            "Count": True,
            "Date_Numeric_Reversed": False,
        },
        title=title,
        labels={
            "Position": "Location",
            "Display_ID": "Train",
            "Date_Numeric_Reversed": "Date",
            "Count": "Occurrences",
        },
        category_orders={
            "Position": [
                k for k, v in sorted(location_order.items(), key=lambda x: x[1])
            ],
            "Display_ID": train_order,
        },
        color_continuous_scale="Viridis",
        range_color=[0, 1],
    )

    fig.update_traces(
        marker=dict(
            sizemin=8,
            line=dict(width=1, color="white"),
        )
    )

    n_ticks = min(10, len(unique_dates))
    tick_vals = [i / (n_ticks - 1) for i in range(n_ticks)] if n_ticks > 1 else [0]
    tick_labels = [
        str(unique_dates[len(unique_dates) - 1 - int(v * (len(unique_dates) - 1))])
        for v in tick_vals
    ]

    fig.update_layout(
        xaxis_tickangle=-45,
        height=max(500, len(train_order) * 15),
        xaxis_title="Location (Sequential Order)",
        yaxis_title="Train ID",
        coloraxis_colorbar=dict(
            title="Date",
            tickvals=tick_vals,
            ticktext=tick_labels,
        ),
    )

    return fig


def create_train_bar_chart(
    df: pd.DataFrame, title: str = "Slip Count by Train"
) -> go.Figure:
    if df.empty:
        return go.Figure()

    df = df.copy()
    df = get_date_normalized(df)

    train_counts = (
        df.groupby(["Display_ID", "Date", "Date_Numeric"])
        .size()
        .reset_index(name="Count")
    )
    train_totals = (
        train_counts.groupby("Display_ID")["Count"].sum().sort_values(ascending=False)
    )
    train_order = train_totals.index.tolist()

    unique_dates = sorted(train_counts["Date"].unique())

    fig = go.Figure()

    for date in unique_dates:
        date_data = train_counts[train_counts["Date"] == date]
        date_numeric = date_data["Date_Numeric"].iloc[0]

        color_val = cm.viridis(1 - date_numeric)

        fig.add_trace(
            go.Bar(
                name=str(date),
                x=date_data["Display_ID"],
                y=date_data["Count"],
                marker_color=f"rgb({int(color_val[0] * 255)}, {int(color_val[1] * 255)}, {int(color_val[2] * 255)})",
                showlegend=False,
            )
        )

    n_ticks = min(10, len(unique_dates))
    tick_vals = [i / (n_ticks - 1) for i in range(n_ticks)] if n_ticks > 1 else [0]
    tick_labels = [
        str(unique_dates[len(unique_dates) - 1 - int(v * (len(unique_dates) - 1))])
        for v in tick_vals
    ]

    fig.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            marker=dict(
                colorscale="Viridis",
                cmin=0,
                cmax=1,
                colorbar=dict(
                    title="Date",
                    tickvals=tick_vals,
                    ticktext=tick_labels,
                    len=0.75,
                    outlinewidth=0,
                ),
                showscale=True,
            ),
            hoverinfo="none",
            showlegend=False,
        )
    )

    fig.update_layout(
        barmode="stack",
        title=title,
        xaxis_tickangle=-45,
        height=500,
        xaxis_title="Train ID",
        yaxis_title="Number of Slip Occurrences",
        xaxis={"categoryorder": "array", "categoryarray": train_order},
    )

    return fig


def create_location_bar_chart(
    df: pd.DataFrame, title: str = "Slip Count by Location"
) -> go.Figure:
    if df.empty:
        return go.Figure()

    df = df.copy()
    df = get_date_normalized(df)

    location_counts = (
        df.groupby(["Position", "Date", "Date_Numeric"])
        .size()
        .reset_index(name="Count")
    )
    location_totals = (
        location_counts.groupby("Position")["Count"].sum().sort_values(ascending=False)
    )
    location_order = location_totals.index.tolist()

    unique_dates = sorted(location_counts["Date"].unique())

    fig = go.Figure()

    for date in unique_dates:
        date_data = location_counts[location_counts["Date"] == date]
        date_numeric = date_data["Date_Numeric"].iloc[0]

        color_val = cm.viridis(1 - date_numeric)

        fig.add_trace(
            go.Bar(
                name=str(date),
                x=date_data["Position"],
                y=date_data["Count"],
                marker_color=f"rgb({int(color_val[0] * 255)}, {int(color_val[1] * 255)}, {int(color_val[2] * 255)})",
                showlegend=False,
            )
        )

    n_ticks = min(10, len(unique_dates))
    tick_vals = [i / (n_ticks - 1) for i in range(n_ticks)] if n_ticks > 1 else [0]
    tick_labels = [
        str(unique_dates[len(unique_dates) - 1 - int(v * (len(unique_dates) - 1))])
        for v in tick_vals
    ]

    fig.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            marker=dict(
                colorscale="Viridis",
                cmin=0,
                cmax=1,
                colorbar=dict(
                    title="Date",
                    tickvals=tick_vals,
                    ticktext=tick_labels,
                    len=0.75,
                    outlinewidth=0,
                ),
                showscale=True,
            ),
            hoverinfo="none",
            showlegend=False,
        )
    )

    fig.update_layout(
        barmode="stack",
        title=title,
        xaxis_tickangle=-45,
        height=500,
        xaxis_title="Location",
        yaxis_title="Number of Slip Occurrences",
        xaxis={"categoryorder": "array", "categoryarray": location_order},
    )

    return fig


def create_date_bar_chart(
    df: pd.DataFrame, title: str = "Slip Count by Date"
) -> go.Figure:
    if df.empty:
        return go.Figure()

    df = df.copy()

    date_counts = df.groupby(["Date", "Display_ID"]).size().reset_index(name="Count")
    date_order = sorted(date_counts["Date"].unique())
    train_order = sorted(
        date_counts["Display_ID"].unique(), key=lambda x: (len(str(x)), str(x))
    )

    fig = px.bar(
        date_counts,
        x="Date",
        y="Count",
        color="Display_ID",
        title=title,
        labels={
            "Date": "Date",
            "Count": "Number of Slips",
            "Display_ID": "Train ID",
        },
        category_orders={"Date": date_order, "Display_ID": train_order},
    )

    fig.update_layout(
        xaxis_tickangle=-45,
        height=500,
        xaxis_title="Date",
        yaxis_title="Number of Slip Occurrences",
        barmode="stack",
        legend_title_text="Train ID",
    )

    return fig


def create_heatmap_train_location(
    df: pd.DataFrame,
    location_order: Dict[str, int],
    title: str = "Correlation: Train vs Location",
) -> go.Figure:
    if df.empty:
        return go.Figure()

    df = df.copy()
    df["Location_Order"] = df["Position"].map(location_order)
    df = df.dropna(subset=["Location_Order"])

    pivot = df.pivot_table(
        index="Display_ID",
        columns="Position",
        values="Logger Datetime",
        aggfunc="count",
        fill_value=0,
    )

    sorted_locations = [
        k
        for k, v in sorted(location_order.items(), key=lambda x: x[1])
        if k in pivot.columns
    ]
    pivot = pivot[sorted_locations]

    fig = px.imshow(
        pivot,
        title=title,
        labels=dict(x="Location", y="Train ID", color="Slip Count"),
        color_continuous_scale="Blues",
    )

    fig.update_layout(height=max(500, len(pivot.index) * 15), xaxis_tickangle=-45)

    return fig


def create_heatmap_train_time(
    df: pd.DataFrame, title: str = "Correlation: Train vs Time of Day"
) -> go.Figure:
    if df.empty:
        return go.Figure()

    df = df.copy()
    df["Hour"] = df["Logger Datetime"].dt.hour

    pivot = df.pivot_table(
        index="Display_ID",
        columns="Hour",
        values="Logger Datetime",
        aggfunc="count",
        fill_value=0,
    )

    for h in range(24):
        if h not in pivot.columns:
            pivot[h] = 0
    pivot = pivot.reindex(columns=sorted(pivot.columns))

    fig = px.imshow(
        pivot,
        title=title,
        labels=dict(x="Hour of Day", y="Train ID", color="Slip Count"),
        color_continuous_scale="Blues",
    )

    fig.update_layout(
        height=max(500, len(pivot.index) * 15),
        xaxis=dict(tickmode="linear", tick0=0, dtick=1),
    )

    return fig


def create_heatmap_location_time(
    df: pd.DataFrame,
    location_order: Dict[str, int],
    title: str = "Correlation: Location vs Time of Day",
) -> go.Figure:
    if df.empty:
        return go.Figure()

    df = df.copy()
    df["Hour"] = df["Logger Datetime"].dt.hour
    df["Location_Order"] = df["Position"].map(location_order)
    df = df.dropna(subset=["Location_Order"])

    pivot = df.pivot_table(
        index="Position",
        columns="Hour",
        values="Logger Datetime",
        aggfunc="count",
        fill_value=0,
    )

    sorted_locations = [
        k
        for k, v in sorted(location_order.items(), key=lambda x: x[1])
        if k in pivot.index
    ]
    pivot = pivot.reindex(sorted_locations)

    for h in range(24):
        if h not in pivot.columns:
            pivot[h] = 0
    pivot = pivot.reindex(columns=sorted(pivot.columns))

    fig = px.imshow(
        pivot,
        title=title,
        labels=dict(x="Hour of Day", y="Location", color="Slip Count"),
        color_continuous_scale="Blues",
    )

    fig.update_layout(
        height=max(500, len(pivot.index) * 12),
        xaxis=dict(tickmode="linear", tick0=0, dtick=1),
        yaxis_tickangle=-45,
    )

    return fig


def create_heatmap_train_rainfall(
    df: pd.DataFrame,
    rainfall_data: pd.DataFrame,
    title: str = "Correlation: Train vs Rainfall",
) -> go.Figure:
    if df.empty or rainfall_data.empty:
        return go.Figure()

    df = df.copy()
    rainfall_data = rainfall_data.copy()

    rainfall_data["DateObj"] = rainfall_data["Date"].dt.date
    df["DateObj"] = df["Date"]

    df = df.merge(rainfall_data[["DateObj", "Rainfall"]], on="DateObj", how="left")
    df["Rainfall"] = df["Rainfall"].fillna(0)

    bins = [0, 0.1, 10, 25, 50, 100, float("inf")]
    labels = ["0", "0.1-10", "10-25", "25-50", "50-100", "100+"]
    df["Rainfall_Bin"] = pd.cut(
        df["Rainfall"], bins=bins, labels=labels, include_lowest=True
    )

    pivot = df.pivot_table(
        index="Display_ID",
        columns="Rainfall_Bin",
        values="Logger Datetime",
        aggfunc="count",
        fill_value=0,
    )

    for lbl in labels:
        if lbl not in pivot.columns:
            pivot[lbl] = 0
    pivot = pivot[labels]

    fig = px.imshow(
        pivot,
        title=title,
        labels=dict(x="Rainfall (mm)", y="Train ID", color="Slip Count"),
        color_continuous_scale="Blues",
    )

    fig.update_layout(
        height=max(500, len(pivot.index) * 15),
        xaxis_tickangle=-45,
    )

    return fig


def create_heatmap_location_rainfall(
    df: pd.DataFrame,
    location_order: Dict[str, int],
    rainfall_data: pd.DataFrame,
    title: str = "Correlation: Location vs Rainfall",
) -> go.Figure:
    if df.empty or rainfall_data.empty:
        return go.Figure()

    df = df.copy()
    rainfall_data = rainfall_data.copy()
    df["Location_Order"] = df["Position"].map(location_order)
    df = df.dropna(subset=["Location_Order"])

    rainfall_data["DateObj"] = rainfall_data["Date"].dt.date
    df["DateObj"] = df["Date"]

    df = df.merge(rainfall_data[["DateObj", "Rainfall"]], on="DateObj", how="left")
    df["Rainfall"] = df["Rainfall"].fillna(0)

    bins = [0, 0.1, 10, 25, 50, 100, float("inf")]
    labels = ["0", "0.1-10", "10-25", "25-50", "50-100", "100+"]
    df["Rainfall_Bin"] = pd.cut(
        df["Rainfall"], bins=bins, labels=labels, include_lowest=True
    )

    pivot = df.pivot_table(
        index="Position",
        columns="Rainfall_Bin",
        values="Logger Datetime",
        aggfunc="count",
        fill_value=0,
    )

    sorted_locations = [
        k
        for k, v in sorted(location_order.items(), key=lambda x: x[1])
        if k in pivot.index
    ]
    pivot = pivot.reindex(sorted_locations)

    for lbl in labels:
        if lbl not in pivot.columns:
            pivot[lbl] = 0
    pivot = pivot[labels]

    fig = px.imshow(
        pivot,
        title=title,
        labels=dict(x="Rainfall (mm)", y="Location", color="Slip Count"),
        color_continuous_scale="Blues",
    )

    fig.update_layout(
        height=max(500, len(pivot.index) * 12),
        xaxis_tickangle=-45,
        yaxis_tickangle=-45,
    )

    return fig
