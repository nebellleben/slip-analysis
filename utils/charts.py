import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Optional

from utils.data_processor import get_date_normalized


def create_date_location_scatter(
    df: pd.DataFrame,
    location_order: Dict[str, int],
    title: str = "Slip Occurrences: Date vs Location",
    selected_trains: Optional[List[str]] = None,
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
        color="Count",
        title=title,
        labels={
            "Display_ID": "Train ID",
            "Date": "Date",
            "Count": "Occurrences",
        },
        category_orders={"Display_ID": train_order},
        color_continuous_scale="Greys_r",
    )

    fig.update_layout(
        xaxis_tickangle=-45,
        height=500,
        xaxis_title="Train ID",
        yaxis_title="Date",
        coloraxis_colorbar=dict(title="Slip Count"),
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
    df["Location_Order"] = df["Position"].map(location_order)
    df = df.dropna(subset=["Location_Order"])

    if sort_by_frequency:
        train_counts = df.groupby("Display_ID").size().sort_values(ascending=True)
        train_order = train_counts.index.tolist()
    else:
        train_order = sorted(
            df["Display_ID"].unique(), key=lambda x: (len(str(x)), str(x))
        )

    fig = px.scatter(
        df,
        x="Position",
        y="Display_ID",
        color="Date",
        title=title,
        labels={
            "Position": "Location",
            "Display_ID": "Train",
            "Date": "Date",
        },
        category_orders={
            "Position": [
                k for k, v in sorted(location_order.items(), key=lambda x: x[1])
            ],
            "Display_ID": train_order,
        },
        color_continuous_scale="Greys_r",
    )

    fig.update_layout(
        xaxis_tickangle=-45,
        height=max(500, len(train_order) * 15),
        xaxis_title="Location (Sequential Order)",
        yaxis_title="Train ID",
        coloraxis_colorbar=dict(title="Date (darker=newer)"),
    )

    return fig


def create_train_bar_chart(
    df: pd.DataFrame, title: str = "Slip Count by Train"
) -> go.Figure:
    if df.empty:
        return go.Figure()

    df = df.copy()

    train_counts = (
        df.groupby("Display_ID")
        .agg(Count=("Display_ID", "size"), Avg_Date=("Date", "first"))
        .reset_index()
    )
    train_counts = train_counts.sort_values("Count", ascending=False)

    fig = px.bar(
        train_counts,
        x="Display_ID",
        y="Count",
        color="Avg_Date",
        title=title,
        labels={
            "Display_ID": "Train ID",
            "Count": "Number of Slips",
            "Avg_Date": "Date",
        },
        color_continuous_scale="Greys_r",
    )

    fig.update_layout(
        xaxis_tickangle=-45,
        height=500,
        xaxis_title="Train ID",
        yaxis_title="Number of Slip Occurrences",
        coloraxis_colorbar=dict(title="Date (darker=newer)"),
    )

    return fig


def create_location_bar_chart(
    df: pd.DataFrame, title: str = "Slip Count by Location"
) -> go.Figure:
    if df.empty:
        return go.Figure()

    df = df.copy()

    location_counts = (
        df.groupby("Position")
        .agg(Count=("Position", "size"), Avg_Date=("Date", "first"))
        .reset_index()
    )
    location_counts = location_counts.sort_values("Count", ascending=False)

    fig = px.bar(
        location_counts,
        x="Position",
        y="Count",
        color="Avg_Date",
        title=title,
        labels={"Position": "Location", "Count": "Number of Slips", "Avg_Date": "Date"},
        color_continuous_scale="Greys_r",
    )

    fig.update_layout(
        xaxis_tickangle=-45,
        height=500,
        xaxis_title="Location (VCC/LOOP)",
        yaxis_title="Number of Slip Occurrences",
        coloraxis_colorbar=dict(title="Date (darker=newer)"),
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
