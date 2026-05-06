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

@st.cache_data
def load_budgets() -> pd.DataFrame:
    path = get_data_path("budgets.json")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    df = pd.DataFrame(data)
    df["budget"] = pd.to_numeric(df["budget"])
    return df

transactions_df = load_transactions()
budgets_df = load_budgets()
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

if filtered_category_rows.empty:
    st.warning("No data for this category in the selected timeframe.")
    st.stop()

chart_df = ()

historical_chart = (
    alt.Chart(chart_df)
    .mark_line(point=True)
    .encode(
        x=alt.X(
            "date:T",
            title=None,
            axis=alt.Axis(format="%b %d", labelAngle=0)
        ),
        y=alt.Y(
            "amount:Q",
            title="Amount"
        ),
        tooltip=[
            alt.Tooltip("date:T", title="Date"),
            alt.Tooltip("amount:Q", title="Amount", format=",.2f")
        ]
    )
    .properties(height=360)
    .interactive()
)

st.altair_chart(historical_chart, use_container_width=True)

controls_left, controls_right = st.columns([3, 1])


with controls_left:
    new_tf = st.segmented_control(
        "Timeframe",
        TIMEFRAMES,
        default=page_tf,
        label_visibility="collapsed"
    )

    new_tf = new_tf or "M"

    if new_tf != st.session_state["category_info_tf"]:
        st.session_state["category_info_tf"] = new_tf
        st.rerun()

with controls_right:
    st.page_link("data_entry.py", label="+ New Data", icon="➕")

stats_col, comparison_col = st.columns(2)

# Stats  for selected category listed on the left side of page
total_amount = filtered_category_rows["amount"].sum()
avg_amount = filtered_category_rows["amount"].mean()
median_amount = filtered_category_rows["amount"].median()
max_amount = filtered_category_rows["amount"].max()
min_amount = filtered_category_rows["amount"].min()
frequency = len(filtered_category_rows)
std_amount = filtered_category_rows["amount"].std()

with stats_col:
    st.subheader("Stats")

    s1, s2 = st.columns(2)
    s1.metric("Sum", f"${total_amount:,.2f}")
    s2.metric("Average", f"${avg_amount:,.2f}")

    s3, s4 = st.columns(2)
    s3.metric("Median", f"${median_amount:,.2f}")
    s4.metric("Frequency", f"{frequency}")

    s5, s6 = st.columns(2)
    s5.metric("Max", f"${max_amount:,.2f}")
    s6.metric("Min", f"${min_amount:,.2f}")

    st.metric("Volatility", f"${std_amount:,.2f}")

# Data for comparison chart and information
same_group_rows = filtered_transactions[
    filtered_transactions["group"] == selected_group
].copy()

comparison_df = (
    same_group_rows.groupby("category", as_index=False)["amount"]
    .sum()
    .sort_values("amount", ascending=False)
)

selected_total = comparison_df.loc[
    comparison_df["category"] == selected_category, "amount"
].sum()

group_total = comparison_df["amount"].sum()
other_total = group_total - selected_total
portion = (selected_total / group_total * 100) if group_total > 0 else 0

comparison_df = comparison_df.reset_index(drop=True)
standing = comparison_df.index[comparison_df["category"] == selected_category][0] + 1