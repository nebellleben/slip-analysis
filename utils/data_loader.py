import pandas as pd
from typing import Tuple, Optional
import io


def load_alarm_data(
    file_path: str = "resources/alarm_message_data_user_5.csv",
) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    df["Logger Datetime"] = pd.to_datetime(df["Logger Datetime"])
    df["Server Datetime"] = pd.to_datetime(df["Server Datetime"])
    return df


def load_alarm_data_from_upload(uploaded_file) -> pd.DataFrame:
    content = uploaded_file.read()
    df = pd.read_csv(io.BytesIO(content))
    df["Logger Datetime"] = pd.to_datetime(df["Logger Datetime"])
    df["Server Datetime"] = pd.to_datetime(df["Server Datetime"])
    return df


def load_loop_sequence(
    file_path: str = "resources/loop_sequence.xlsx",
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    xl = pd.ExcelFile(file_path)
    dt_sequence = pd.read_excel(xl, sheet_name="DT")
    ut_sequence = pd.read_excel(xl, sheet_name="UT")
    dt_sequence["Location"] = (
        "VCC"
        + dt_sequence["VCC"].astype(str)
        + " / LOOP"
        + dt_sequence["Loop"].astype(str)
    )
    ut_sequence["Location"] = (
        "VCC"
        + ut_sequence["VCC"].astype(str)
        + " / LOOP"
        + ut_sequence["Loop"].astype(str)
    )
    return dt_sequence, ut_sequence


def load_train_id_mapping(
    file_path: str = "resources/TML_Train_ID_Formation.xlsx",
) -> pd.DataFrame:
    df = pd.read_excel(file_path)
    return df
