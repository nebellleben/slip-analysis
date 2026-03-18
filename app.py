import streamlit as st
import pandas as pd
from datetime import datetime
import io

from utils.data_loader import (
    load_alarm_data,
    load_alarm_data_from_upload,
    load_loop_sequence,
    load_train_id_mapping,
)
from utils.data_processor import (
    build_location_order_map,
    get_valid_locations,
    filter_valid_locations,
    infer_direction,
    deduplicate_slips,
    build_id_mapping,
    convert_id,
    filter_by_date_range,
    filter_by_direction,
)
from utils.charts import (
    create_date_location_scatter,
    create_date_train_scatter,
    create_train_location_scatter,
    create_train_bar_chart,
    create_location_bar_chart,
    create_date_bar_chart,
    create_heatmap_train_location,
    create_heatmap_train_time,
    create_heatmap_location_time,
)

st.set_page_config(page_title="Slip Analysis Dashboard", page_icon="🚇", layout="wide")

st.title("Slip Analysis Dashboard")


@st.cache_data
def load_data():
    alarm_df = load_alarm_data()
    dt_seq, ut_seq = load_loop_sequence()
    train_mapping = load_train_id_mapping()
    return alarm_df, dt_seq, ut_seq, train_mapping


alarm_df, dt_seq, ut_seq, train_mapping = load_data()
alarm_df["Date"] = alarm_df["Logger Datetime"].dt.date

min_date = alarm_df["Date"].min()
max_date = alarm_df["Date"].max()

date_range = st.sidebar.slider(
    "Date Range",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date),
    format="YYYY-MM-DD",
)

st.sidebar.subheader("Direction")
show_down = st.sidebar.checkbox("Down (DT)", value=True)
show_up = st.sidebar.checkbox("Up (UT)", value=True)

if not show_down and not show_up:
    st.warning("Please select at least one direction.")
    st.stop()

id_type = st.sidebar.selectbox(
    "ID Type", options=["Train ID", "Cab ID", "VOBC"], index=0
)

dt_order, ut_order = build_location_order_map(dt_seq, ut_seq)

valid_locations = get_valid_locations(dt_seq, ut_seq)
df = filter_valid_locations(alarm_df, valid_locations)
df = infer_direction(df, dt_seq, ut_seq)
df = deduplicate_slips(df)

id_mapping = build_id_mapping(train_mapping)

df = convert_id(df, id_type, id_mapping)
df_dt = df[df["Direction"].isin(["DT", "BOTH"])]
df_ut = df[df["Direction"].isin(["UT", "BOTH"])]

st.sidebar.metric("Total Records", len(df))

df_dt = df[df["Direction"].isin(["DT", "BOTH"])]
df_ut = df[df["Direction"].isin(["UT", "BOTH"])]

st.header("Dashboard 1: Date vs Location")
show_all_trains = st.checkbox("Show all trains", value=True, key="d1_all_trains")

selected_trains_d1 = None
if not show_all_trains:
    all_trains = sorted(df["Display_ID"].unique())
    selected_trains_d1 = st.multiselect(
        "Select trains",
        options=all_trains,
        default=all_trains[:5] if len(all_trains) > 5 else all_trains,
        key="d1_trains",
    )

if show_down and show_up:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Down Direction")
        fig1_dt = create_date_location_scatter(
            df_dt, dt_order, "Date vs Location (Down)", selected_trains_d1
        )
        st.plotly_chart(fig1_dt, use_container_width=True)
    with col2:
        st.subheader("Up Direction")
        fig1_ut = create_date_location_scatter(
            df_ut, ut_order, "Date vs Location (Up)", selected_trains_d1
        )
        st.plotly_chart(fig1_ut, use_container_width=True)
elif show_down:
    fig1 = create_date_location_scatter(
        df_dt, dt_order, "Date vs Location (Down)", selected_trains_d1
    )
    st.plotly_chart(fig1, use_container_width=True)
elif show_up:
    fig1 = create_date_location_scatter(
        df_ut, ut_order, "Date vs Location (Up)", selected_trains_d1
    )
    st.plotly_chart(fig1, use_container_width=True)

st.divider()

st.header("Dashboard 2: Date vs Train")
show_all_trains_d2 = st.checkbox("Show all trains", value=True, key="d2_all_trains")

selected_trains_d2 = None
if not show_all_trains_d2:
    all_trains = sorted(df["Display_ID"].unique())
    selected_trains_d2 = st.multiselect(
        "Select trains",
        options=all_trains,
        default=all_trains[:5] if len(all_trains) > 5 else all_trains,
        key="d2_trains",
    )
if show_down and show_up:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Down Direction")
        fig2_dt = create_date_train_scatter(
            df_dt, "Date vs Train (Down)", selected_trains_d2
        )
        st.plotly_chart(fig2_dt, use_container_width=True)
    with col2:
        st.subheader("Up Direction")
        fig2_ut = create_date_train_scatter(
            df_ut, "Date vs Train (Up)", selected_trains_d2
        )
        st.plotly_chart(fig2_ut, use_container_width=True)
elif show_down:
    fig2 = create_date_train_scatter(df_dt, "Date vs Train (Down)", selected_trains_d2)
    st.plotly_chart(fig2, use_container_width=True)
elif show_up:
    fig2 = create_date_train_scatter(df_ut, "Date vs Train (Up)", selected_trains_d2)
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

st.header("Dashboard 3: Train vs Location")
sort_by_freq = st.checkbox(
    "Sort trains by slip frequency (ascending)", value=False, key="d3_sort_freq"
)

if show_down and show_up:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Down Direction")
        fig3_dt = create_train_location_scatter(
            df_dt, dt_order, "Train vs Location (Down)", sort_by_freq
        )
        st.plotly_chart(fig3_dt, use_container_width=True)
    with col2:
        st.subheader("Up Direction")
        fig3_ut = create_train_location_scatter(
            df_ut, ut_order, "Train vs Location (Up)", sort_by_freq
        )
        st.plotly_chart(fig3_ut, use_container_width=True)
elif show_down:
    fig3 = create_train_location_scatter(
        df_dt, dt_order, "Train vs Location (Down)", sort_by_freq
    )
    st.plotly_chart(fig3, use_container_width=True)
elif show_up:
    fig3 = create_train_location_scatter(
        df_ut, ut_order, "Train vs Location (Up)", sort_by_freq
    )
    st.plotly_chart(fig3, use_container_width=True)

st.divider()

st.header("Dashboard 4: Slip Count by Train")
if show_down and show_up:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Down Direction")
        fig4_dt = create_train_bar_chart(df_dt, "Slip Count by Train (Down)")
        st.plotly_chart(fig4_dt, use_container_width=True)
    with col2:
        st.subheader("Up Direction")
        fig4_ut = create_train_bar_chart(df_ut, "Slip Count by Train (Up)")
        st.plotly_chart(fig4_ut, use_container_width=True)
elif show_down:
    fig4 = create_train_bar_chart(df_dt, "Slip Count by Train (Down)")
    st.plotly_chart(fig4, use_container_width=True)
elif show_up:
    fig4 = create_train_bar_chart(df_ut, "Slip Count by Train (Up)")
    st.plotly_chart(fig4, use_container_width=True)

st.divider()

st.header("Dashboard 5: Slip Count by Location")
if show_down and show_up:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Down Direction")
        fig5_dt = create_location_bar_chart(df_dt, "Slip Count by Location (Down)")
        st.plotly_chart(fig5_dt, use_container_width=True)
    with col2:
        st.subheader("Up Direction")
        fig5_ut = create_location_bar_chart(df_ut, "Slip Count by Location (Up)")
        st.plotly_chart(fig5_ut, use_container_width=True)
elif show_down:
    fig5 = create_location_bar_chart(df_dt, "Slip Count by Location (Down)")
    st.plotly_chart(fig5, use_container_width=True)
elif show_up:
    fig5 = create_location_bar_chart(df_ut, "Slip Count by Location (Up)")
    st.plotly_chart(fig5, use_container_width=True)

st.divider()

st.header("Dashboard 5b: Slip Count by Date")
if show_down and show_up:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Down Direction")
        fig5b_dt = create_date_bar_chart(df_dt, "Slip Count by Date (Down)")
        st.plotly_chart(fig5b_dt, use_container_width=True)
    with col2:
        st.subheader("Up Direction")
        fig5b_ut = create_date_bar_chart(df_ut, "Slip Count by Date (Up)")
        st.plotly_chart(fig5b_ut, use_container_width=True)
elif show_down:
    fig5b = create_date_bar_chart(df_dt, "Slip Count by Date (Down)")
    st.plotly_chart(fig5b, use_container_width=True)
elif show_up:
    fig5b = create_date_bar_chart(df_ut, "Slip Count by Date (Up)")
    st.plotly_chart(fig5b, use_container_width=True)

st.divider()

st.header("Dashboard 6: Correlation Heatmaps")

st.subheader("A. Train vs Location")
if show_down and show_up:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Down Direction**")
        fig6a_dt = create_heatmap_train_location(
            df_dt, dt_order, "Train vs Location (Down)"
        )
        st.plotly_chart(fig6a_dt, use_container_width=True)
    with col2:
        st.markdown("**Up Direction**")
        fig6a_ut = create_heatmap_train_location(
            df_ut, ut_order, "Train vs Location (Up)"
        )
        st.plotly_chart(fig6a_ut, use_container_width=True)
elif show_down:
    fig6a = create_heatmap_train_location(df_dt, dt_order, "Train vs Location (Down)")
    st.plotly_chart(fig6a, use_container_width=True)
elif show_up:
    fig6a = create_heatmap_train_location(df_ut, ut_order, "Train vs Location (Up)")
    st.plotly_chart(fig6a, use_container_width=True)

st.subheader("B. Train vs Time of Day")
if show_down and show_up:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Down Direction**")
        fig6b_dt = create_heatmap_train_time(df_dt, "Train vs Time of Day (Down)")
        st.plotly_chart(fig6b_dt, use_container_width=True)
    with col2:
        st.markdown("**Up Direction**")
        fig6b_ut = create_heatmap_train_time(df_ut, "Train vs Time of Day (Up)")
        st.plotly_chart(fig6b_ut, use_container_width=True)
elif show_down:
    fig6b = create_heatmap_train_time(df_dt, "Train vs Time of Day (Down)")
    st.plotly_chart(fig6b, use_container_width=True)
elif show_up:
    fig6b = create_heatmap_train_time(df_ut, "Train vs Time of Day (Up)")
    st.plotly_chart(fig6b, use_container_width=True)

st.subheader("C. Location vs Time of Day")
if show_down and show_up:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Down Direction**")
        fig6c_dt = create_heatmap_location_time(
            df_dt, dt_order, "Location vs Time of Day (Down)"
        )
        st.plotly_chart(fig6c_dt, use_container_width=True)
    with col2:
        st.markdown("**Up Direction**")
        fig6c_ut = create_heatmap_location_time(
            df_ut, ut_order, "Location vs Time of Day (Up)"
        )
        st.plotly_chart(fig6c_ut, use_container_width=True)
elif show_down:
    fig6c = create_heatmap_location_time(
        df_dt, dt_order, "Location vs Time of Day (Down)"
    )
    st.plotly_chart(fig6c, use_container_width=True)
elif show_up:
    fig6c = create_heatmap_location_time(
        df_ut, ut_order, "Location vs Time of Day (Up)"
    )
    st.plotly_chart(fig6c, use_container_width=True)

st.divider()

st.header("Dashboard 7: Slip Records Table")

col_filter1, col_filter2 = st.columns(2)

with col_filter1:
    st.subheader("Filter by location")
    all_locations = sorted(df["Position"].unique())
    selected_locations = st.multiselect(
        "Filter by location",
        options=all_locations,
        default=[],
        key="table_locations",
    )
with col_filter2:
    st.subheader(f"Filter by {id_type}")
    all_ids = sorted(df["Display_ID"].unique(), key=lambda x: (len(str(x)), str(x)))
    selected_ids = st.multiselect(
        f"Filter by {id_type}", options=all_ids, default=[], key="table_ids"
    )
table_df = df.copy()
if selected_locations:
    table_df = table_df[table_df["Position"].isin(selected_locations)]
if selected_ids:
    table_df = table_df[table_df["Display_ID"].isin(selected_ids)]
display_columns = [
    "Logger Datetime",
    "Server Datetime",
    "Display_ID",
    "Position",
    "Pos",
    "VOBC Status",
    "Detail",
    "Alarm Level",
]
st.dataframe(
    table_df[display_columns],
    use_container_width=True,
    hide_index=True,
    column_config={
        "Logger Datetime": st.column_config.DatetimeColumn(
            "Logger Datetime", format="YYYY-MM-DD HH:mm:ss"
        ),
        "Server Datetime": st.column_config.DatetimeColumn(
            "Server Datetime", format="YYYY-MM-DD HH:mm:ss"
        ),
    },
)
st.caption(f"Showing {len(table_df)} records (filtered from {len(df)} total)")
