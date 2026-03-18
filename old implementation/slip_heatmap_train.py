import pandas as pd
import altair as alt

df = pd.read_csv("alarm_message_data_user_5.csv")

df["Date"] = pd.to_datetime(df["Server Datetime"]).dt.strftime("%Y-%m-%d")
df["Location"] = df["Position"]

df_unique = df.drop_duplicates(subset=["Date", "Train", "Location"])

agg_data = (
    df_unique.groupby(["Location", "Train", "Date"]).size().reset_index(name="count")
)

trains = sorted(agg_data["Train"].unique().tolist())
locations = sorted(agg_data["Location"].unique().tolist())
dates = sorted(agg_data["Date"].unique().tolist())

train_dropdown = alt.binding_select(options=trains, name="Select Train: ")
train_select = alt.selection_point(fields=["Train"], bind=train_dropdown, name="Train")

heatmap_all = (
    alt.Chart(agg_data)
    .mark_rect()
    .encode(
        x=alt.X("Date:N", title="Date", sort=dates),
        y=alt.Y("Location:N", title="Location (VCC / LOOP)", sort=locations),
        color=alt.Color(
            "count:Q",
            title="Slip Count",
            scale=alt.Scale(scheme="redyellowgreen", reverse=True),
        ),
        tooltip=["Location", "Train", "Date", "count"],
    )
    .properties(
        width=900,
        height=600,
        title="Slip Occurrences: Location vs Date (All Trains)",
    )
)

legend_selection = alt.selection_point(fields=["Train"], bind="legend")

scatter_filtered = (
    alt.Chart(agg_data)
    .mark_circle(size=60)
    .encode(
        x=alt.X("Date:N", title="Date", sort=dates),
        y=alt.Y("Location:N", title="Location", sort=locations),
        color=alt.Color(
            "Train:N",
            title="Train (click legend)",
            scale=alt.Scale(scheme="category20"),
        ),
        size=alt.Size("count:Q", title="Count", scale=alt.Scale(range=[50, 300])),
        opacity=alt.condition(legend_selection, alt.value(1), alt.value(0.1)),
        tooltip=[
            "Location",
            "Train",
            "Date",
            alt.Tooltip("count:Q", title="Occurrences"),
        ],
    )
    .add_params(legend_selection)
    .properties(
        width=900,
        height=600,
        title="Interactive 3D: Location × Date × Train (click legend to highlight)",
    )
)

train_rank_data = (
    agg_data.groupby("Train")
    .size()
    .reset_index(name="total")
    .sort_values("total", ascending=False)
)
train_order = train_rank_data["Train"].tolist()

rank_bar = (
    alt.Chart(agg_data)
    .mark_bar()
    .encode(
        x=alt.X("Train:N", title="Train", sort=train_order),
        y=alt.Y("count:Q", title="Total Slip Events"),
        color=alt.Color(
            "count:Q",
            scale=alt.Scale(scheme="redyellowgreen", reverse=True),
            legend=None,
        ),
        tooltip=["Train", alt.Tooltip("count:Q", title="Total Events")],
    )
    .transform_aggregate(count="count()", groupby=["Train"])
    .properties(
        width=900, height=300, title="Trains Ranked by Slip Occurrences (Descending)"
    )
)

brush = alt.selection_interval(encodings=["x", "y"])

location_train_overview = (
    alt.Chart(agg_data)
    .mark_rect()
    .encode(
        x=alt.X("Train:N", title="Train", sort=trains),
        y=alt.Y("Location:N", title="Location", sort=locations),
        color=alt.Color(
            "count:Q",
            title="Count",
            scale=alt.Scale(scheme="redyellowgreen", reverse=True),
        ),
        tooltip=["Location", "Train", alt.Tooltip("count:Q", title="Occurrences")],
    )
    .transform_aggregate(count="count()", groupby=["Location", "Train"])
    .add_params(brush)
    .properties(
        width=900, height=600, title="Overview: Location vs Train (brush to filter)"
    )
)

train_bar = (
    alt.Chart(agg_data)
    .mark_bar()
    .encode(
        x=alt.X("Train:N", title="Train", sort=trains),
        y=alt.Y("count:Q", title="Total Slip Events"),
        color=alt.Color("count:Q", scale=alt.Scale(scheme="reds"), legend=None),
        tooltip=["Train", alt.Tooltip("count:Q", title="Total Events")],
    )
    .transform_aggregate(count="count()", groupby=["Train"])
    .transform_filter(brush)
    .properties(
        width=900, height=200, title="Slip Events by Train (filtered by selection)"
    )
)

date_bar = (
    alt.Chart(agg_data)
    .mark_bar()
    .encode(
        x=alt.X("Date:N", title="Date", sort=dates),
        y=alt.Y("count:Q", title="Total Slip Events"),
        color=alt.Color("count:Q", scale=alt.Scale(scheme="blues"), legend=None),
        tooltip=["Date", alt.Tooltip("count:Q", title="Total Events")],
    )
    .transform_aggregate(count="count()", groupby=["Date"])
    .properties(width=900, height=150, title="Slip Events by Date (All Trains)")
)

date_bar_filtered = (
    alt.Chart(agg_data)
    .mark_bar()
    .encode(
        x=alt.X("Date:N", title="Date", sort=dates),
        y=alt.Y("count:Q", title="Total Slip Events"),
        color=alt.Color("count:Q", scale=alt.Scale(scheme="oranges"), legend=None),
        tooltip=["Train", "Date", alt.Tooltip("count:Q", title="Total Events")],
    )
    .add_params(train_select)
    .transform_filter(train_select)
    .transform_aggregate(count="count()", groupby=["Date", "Train"])
    .properties(width=900, height=150, title="Slip Events by Date (Filtered by Train)")
)

location_rank_data = (
    agg_data.groupby("Location")
    .size()
    .reset_index(name="total")
    .sort_values("total", ascending=False)
)
location_order = location_rank_data["Location"].tolist()

location_rank_bar = (
    alt.Chart(agg_data)
    .mark_bar()
    .encode(
        x=alt.X("Location:N", title="Location (VCC / LOOP)", sort=location_order),
        y=alt.Y("count:Q", title="Total Slip Events"),
        color=alt.Color(
            "count:Q",
            scale=alt.Scale(scheme="redyellowgreen", reverse=True),
            legend=None,
        ),
        tooltip=["Location", alt.Tooltip("count:Q", title="Total Events")],
    )
    .transform_aggregate(count="count()", groupby=["Location"])
    .properties(
        width=900, height=300, title="Locations Ranked by Slip Occurrences (Descending)"
    )
)

chart = (
    alt.vconcat(
        scatter_filtered,
        heatmap_all,
        rank_bar,
        location_rank_bar,
        alt.hconcat(location_train_overview, train_bar),
        date_bar,
        date_bar_filtered,
    )
    .resolve_scale(color="independent")
    .configure_axis(labelFontSize=10, titleFontSize=12)
    .configure_title(fontSize=14)
    .configure_legend(labelFontSize=10)
)

chart.save("slip_heatmap_train.html")

print("Interactive heatmap saved to: slip_heatmap_train.html")
print(f"\nData summary:")
print(f"- Total slip events: {len(agg_data)}")
print(f"- Date range: {min(dates)} to {max(dates)}")
print(f"- Unique locations: {len(locations)}")
print(f"- Unique trains: {len(trains)}")
