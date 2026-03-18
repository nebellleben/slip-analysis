import pandas as pd
from typing import Tuple, Dict, List, Optional


def build_location_order_map(
    dt_sequence: pd.DataFrame, ut_sequence: pd.DataFrame
) -> Tuple[Dict[str, int], Dict[str, int]]:
    dt_order = {loc: idx for idx, loc in enumerate(dt_sequence["Location"].tolist())}
    ut_order = {loc: idx for idx, loc in enumerate(ut_sequence["Location"].tolist())}
    return dt_order, ut_order


def get_valid_locations(dt_sequence: pd.DataFrame, ut_sequence: pd.DataFrame) -> set:
    dt_locations = set(dt_sequence["Location"].tolist())
    ut_locations = set(ut_sequence["Location"].tolist())
    return dt_locations.union(ut_locations)


def filter_valid_locations(df: pd.DataFrame, valid_locations: set) -> pd.DataFrame:
    return df[df["Position"].isin(valid_locations)].copy()


def infer_direction(
    df: pd.DataFrame, dt_sequence: pd.DataFrame, ut_sequence: pd.DataFrame
) -> pd.DataFrame:
    dt_locations = set(dt_sequence["Location"].tolist())
    ut_locations = set(ut_sequence["Location"].tolist())

    dt_only = dt_locations - ut_locations
    ut_only = ut_locations - dt_locations

    def get_direction(position):
        if position in dt_only:
            return "DT"
        elif position in ut_only:
            return "UT"
        else:
            return "BOTH"

    df = df.copy()
    df["Direction"] = df["Position"].apply(get_direction)
    return df


def deduplicate_slips(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Date"] = df["Logger Datetime"].dt.date
    df["Time"] = df["Logger Datetime"].dt.time
    df["Hour"] = df["Logger Datetime"].dt.hour

    df_dedup = df.drop_duplicates(
        subset=["Logger Datetime", "Train", "Position"], keep="first"
    )
    return df_dedup


def build_id_mapping(train_mapping_df: pd.DataFrame) -> Dict[str, Dict]:
    mapping = {
        "train_to_cab": {},
        "train_to_vobc_up": {},
        "train_to_vobc_down": {},
        "cab_to_train": {},
        "vobc_to_train": {},
        "vobc_up_to_train": {},
        "vobc_down_to_train": {},
    }

    for _, row in train_mapping_df.iterrows():
        train_id = str(row["EMU NO."]).strip()
        if not train_id.startswith("T"):
            train_id = "T" + train_id

        train_id_padded = train_id
        if len(train_id) == 2 and train_id[1].isdigit():
            train_id_padded = "T0" + train_id[1]

        cab_col = "Consists" if "Consists" in train_mapping_df.columns else "Cab No"
        cab_up = (
            str(row.get(cab_col, "")).strip()
            if pd.notna(row.get(cab_col, ""))
            else None
        )

        vobc_up = (
            str(row.get("VOBC no. Up End", "")).strip()
            if pd.notna(row.get("VOBC no. Up End", ""))
            else None
        )
        vobc_down = (
            str(row.get("VOBC no. Down End", "")).strip()
            if pd.notna(row.get("VOBC no. Down End", ""))
            else None
        )

        for tid in [train_id, train_id_padded]:
            if cab_up:
                mapping["train_to_cab"][tid] = cab_up
                mapping["cab_to_train"][cab_up] = tid

            if vobc_up:
                mapping["train_to_vobc_up"][tid] = vobc_up
                mapping["vobc_up_to_train"][vobc_up] = tid
                mapping["vobc_to_train"][vobc_up] = tid

            if vobc_down:
                mapping["train_to_vobc_down"][tid] = vobc_down
                mapping["vobc_down_to_train"][vobc_down] = tid
                mapping["vobc_to_train"][vobc_down] = tid

    return mapping


def convert_id(df: pd.DataFrame, id_type: str, id_mapping: Dict) -> pd.DataFrame:
    df = df.copy()
    train_col = "Train"

    if id_type == "Train ID":
        df["Display_ID"] = df[train_col]
        return df

    if id_type == "Cab ID":
        if "Cab No" in df.columns:
            df["Display_ID"] = df["Cab No"].astype(str)
        else:
            df["Display_ID"] = df[train_col].map(id_mapping["train_to_cab"])
            df["Display_ID"] = df["Display_ID"].fillna(df[train_col])
    elif id_type == "VOBC":
        if "VOBC No." in df.columns:
            df["Display_ID"] = df["VOBC No."].astype(int).astype(str)
        else:
            df["Display_ID"] = df[train_col].map(id_mapping["train_to_vobc_up"])
            df["Display_ID"] = df["Display_ID"].fillna(
                df[train_col].map(id_mapping["train_to_vobc_down"])
            )
            df["Display_ID"] = df["Display_ID"].fillna(df[train_col])
    else:
        df["Display_ID"] = df[train_col]

    return df


def filter_by_date_range(df: pd.DataFrame, min_date, max_date) -> pd.DataFrame:
    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"])
    return df[
        (df["Date"] >= pd.to_datetime(min_date))
        & (df["Date"] <= pd.to_datetime(max_date))
    ]


def filter_by_direction(
    df: pd.DataFrame, show_down: bool, show_up: bool
) -> pd.DataFrame:
    if show_down and show_up:
        return df
    elif show_down:
        return df[df["Direction"].isin(["DT", "BOTH"])]
    elif show_up:
        return df[df["Direction"].isin(["UT", "BOTH"])]
    else:
        return df.head(0)


def get_slip_count_by_train(
    df: pd.DataFrame, id_col: str = "Display_ID"
) -> pd.DataFrame:
    counts = df.groupby(id_col).size().reset_index(name="Count")
    counts = counts.sort_values("Count", ascending=False)
    return counts


def get_slip_count_by_location(df: pd.DataFrame) -> pd.DataFrame:
    counts = df.groupby("Position").size().reset_index(name="Count")
    counts = counts.sort_values("Count", ascending=False)
    return counts


def get_date_normalized(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "Date" not in df.columns:
        df["Date"] = df["Logger Datetime"].dt.date
    date_min = df["Date"].min()
    date_max = df["Date"].max()
    date_range_days = (date_max - date_min).days
    if date_range_days > 0:
        df["Date_Numeric"] = (
            pd.to_datetime(df["Date"]) - pd.to_datetime(date_min)
        ).dt.days / date_range_days
    else:
        df["Date_Numeric"] = 0.0
    return df
