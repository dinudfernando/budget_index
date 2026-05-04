'''This page is for showing detailed information about a particular category '''


import os
import json
from typing import Optional

import altair as alt
import pandas as pd
import streamlit as st

# Path Helper
APP_PATH = os.path.dirname(os.path.abspath(__file__))

def get_data_path(filename: str) -> str:
    return os.path.join(APP_PATH, "data", filename)

st.set_page_config(
    page_title="Category Info",
    page_icon="📉",
    layout="wide"
)

TIMEFRAMES = ["W","M","Y","2Y","5Y"]

@st.cache_data
def load_transactions() -> pd.DataFrame:
    path = get_data_path("transactions.json")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"])
    df["amount"] = pd.to_numeric(df["amount"])
    return df.sort_values("date")

transactions_df = load_transactions()

all_categories = sorted(transactions_df["category"].dropna().unique().tolist())

query_parameters = st.query_params
forwarded_category: Optional[str] = query_parameters.get("category", None)
if forwarded_category not in all_categories:
    forwarded_category = all_categories[0]

selected_category = st.selectbox(
    "Category",
    all_categories,
    index=all_categories.index(forwarded_category)
)

st.query_params["category"] = selected_category