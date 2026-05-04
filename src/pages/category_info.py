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
# Categories are shown based on whether redirected or would default to the first category
all_categories = sorted(transactions_df["category"].dropna().unique().tolist())

query_parameters = st.query_params
forwarded_category: Optional[str] = query_parameters.get("category", None)
if forwarded_category not in all_categories:
    forwarded_category = all_categories[0]

#Category Select Box
selected_category = st.selectbox(
    "Category",
    all_categories,
    index=all_categories.index(forwarded_category)
)

st.query_params["category"] = selected_category

category_rows = transactions_df[transactions_df["category"] == selected_category].copy()
selected_group = category_rows["group"].iloc[0]

st.title(selected_category)
st.caption(selected_group)


def filter_by_timeframe(df: pd.DataFrame, tf: str) -> pd.DataFrame:
    '''Timeframe filter for graph and stats'''
    df = df.copy()
    df = df.sort_values("date")

    end = df["date"].max()

    if tf=="W":
        start = end - pd.Timedelta(days=7)
    elif tf=="M":
        start = end - pd.Timedelta(days=30)
    elif tf=="Y":
        start = end - pd.Timedelta(days=365)
    elif tf=="2Y":
        start = end - pd.Timedelta(days=730)
    elif tf=="5Y":
        start = end - pd.Timedelta(days=1825)
    
    return df[df["date"].between(start,end)].copy()

if "category_info_tf" not in st.session_state:
    st.session_state["category_info_tf"] = "M"

page_tf = st.session_state["category_info_tf"]

filtered_transactions = filter_by_timeframe(transactions_df, page_tf)
filtered_category_rows = filtered_transactions[
    filtered_transactions["category"] == selected_category
].copy()

