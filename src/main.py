# IMPORTS
import os
import json
import pandas as pd
import numpy as np
import streamlit as st
import altair as alt
from typing import Optional

# Path Helper
APP_PATH = os.path.dirname(os.path.abspath(__file__))

def get_data_path(filename: str) -> str:
    return os.path.join(APP_PATH, "data", filename)

# Page Details
st.set_page_config(
    page_title="Budget Index",
    page_icon="🪙",
    layout="wide"
)

# Row Styling(Under works)
st.markdown("""
<style>
div.stButton > button {
    width: 75%;
    text-align: left;
    border-radius: 14px;
    border: 1px solid #e5e7eb;
    background: #ffffff;
    color: #111827;
    padding: 0.85rem 1rem;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04);            
}

div.stButton > button:hover {
    border-color: #d1d5db;
    background: #f9fafb;
}
            
</style>
""", unsafe_allow_html=True)

st.title("At a Glance...")

# Timeframe Switcher
TIMEFRAMES = ["W", "M", "Q", "Y", "2Y", "5Y"]

tf = st.segmented_control(
    "Select a Timeframe",
    TIMEFRAMES,
    default="Y",
    help="Change the window used for all charts and stats"
)

# Data Load
def load_transactions() -> pd.DataFrame:
    path = get_data_path("transactions.json")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"])
    df["amount"] = pd.to_numeric(df["amount"])
    return df


# Timeline Filter

def filter_by_timeframe(df: pd.DataFrame, tf: str) -> pd.DataFrame:
    """Filter transactions by the selected timeframe."""

    if tf is None:
        return df
    
    df = df.copy()
    df = df.sort_values("date")

    end = df["date"].max()

    if tf == "W":
        start = end - pd.Timedelta(days=7)
    elif tf == "M":
        start = end - pd.DateOffset(months=1)
    elif tf == "Q":
        start = end - pd.DateOffset(months=3)
    elif tf == "Y":
        start = end - pd.DateOffset(years=1)
    elif tf == "2Y":
        start = end - pd.DateOffset(years=2)
    else:  # "5Y"
        start = end - pd.DateOffset(years=5)

    return df[df["date"].between(start, end)]


# Budget Timeframe Multiplier
def budget_multiplier(tf: str) -> float:
    """Convert monthly budget into the selected timeframe budget."""
    if tf == "W":
        return 7 / 30.44
    elif tf == "M":
        return 1
    elif tf == "Q":
        return 3
    elif tf == "Y":
        return 12
    elif tf == "2Y":
        return 24
    else:  # "5Y"
        return 60
    
# Budget Load

def load_budgets() -> pd.DataFrame:
    path = get_data_path("budgets.json")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    df = pd.DataFrame(data)
    df["budget"] = pd.to_numeric(df["budget"])
    return df


transactions_df = load_transactions()
tf_value = tf or "Y"

# Filtered time frame
transactions_df = filter_by_timeframe(transactions_df, tf_value)
                                      

budgets_df = load_budgets()

income_mask = transactions_df["group"] == "Income"
expense_mask = transactions_df["group"] == "Expenses"

# Sample Data Metrics
total_income = transactions_df.loc[income_mask, "amount"].sum()
total_expenses = transactions_df.loc[expense_mask, "amount"].sum()
net_cashflow = total_income - total_expenses
savings_rate = (net_cashflow / total_income * 100) if total_income > 0 else 0

#  Pie chart summary
pie_df = pd.DataFrame({
    "Group": ["Income", "Expenses"],
    "Amount": [total_income, total_expenses]
})

pie_chart = (
    alt.Chart(pie_df)
    .mark_arc(innerRadius=55)
    .encode(
        theta=alt.Theta("Amount:Q"),
        color=alt.Color(
            "Group:N",
            scale=alt.Scale(
                domain=["Income", "Expenses"],
                range=["#34c759", "#ff3b30"]
            ),
        ),
        tooltip=["Group:N", alt.Tooltip("Amount:Q", format=",.2f")]
    )
    .properties(height=220)
)

st.altair_chart(pie_chart, width="stretch")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Income", f"${total_income:,.2f}")
col2.metric("Total Expenses", f"${total_expenses:,.2f}")
col3.metric("Net Cash Flow", f"${net_cashflow:,.2f}")
col4.metric("Savings Rate", f"{savings_rate:,.2f}%")

st.divider()

#Watchlist
def build_watchlist(transactions: pd.DataFrame, budgets: pd.DataFrame, tf: str) -> pd.DataFrame:
    """Builds a watchlist based on the transaction and budget datasheets provided"""
    
    watch_df = transactions.copy()

    # All transactions grouped by category and total amounts for each
    grouped = watch_df.groupby(["group", "category"], as_index=False)["amount"].sum()
    
    watchlist_df = pd.merge(grouped, budgets, on="category", how="left")

    watchlist_df = watchlist_df.rename(columns={
        "group": "Group",
        "category": "Category",
        "amount" : "Amount",
        "budget": "Budget"
    })

    #Fill nulls with 0 in budget
    watchlist_df["Budget"] = watchlist_df["Budget"].fillna(0)
    watchlist_df["Budget"] = watchlist_df["Budget"] * budget_multiplier(tf)

    watchlist_df["PctBudget"] = 0.0
    budget_mask = watchlist_df["Budget"] > 0
    watchlist_df.loc[budget_mask, "PctBudget"] = (watchlist_df.loc[budget_mask, "Amount"]/ watchlist_df.loc[budget_mask, "Budget"] * 100)

    # Columns in dashboard & Rounding, Sort
    watchlist_df = watchlist_df[["Group", "Category", "Amount", "PctBudget"]]

    # Rounding amounts
    watchlist_df["Amount"] = watchlist_df["Amount"].round(2)
    watchlist_df["PctBudget"] = watchlist_df["PctBudget"].round(1)

    watchlist_df = watchlist_df.sort_values(by="Category")
    watchlist_df = watchlist_df.sort_values(by="Group")

    return watchlist_df

watchlist_df = build_watchlist(transactions_df, budgets_df, tf_value)

# Trend Data/ sparkline
def build_trend_data(transactions: pd.DataFrame) -> pd.DataFrame:
    """Builds data for sparkline under Watchlist"""

    trend_df = transactions.copy()

    trend_df["Month"] = trend_df["date"].dt.to_period("M").astype(str)

    # Grouping transactions
    trend_df = trend_df.groupby(["category", "Month"])["amount"].sum().reset_index()


    return trend_df

trend_df = build_trend_data(transactions_df)

def budget_pct_color(pct: float) -> str:
    """Returns color for budget usage percentage"""
    if pct >= 200:
        return "#7f1d1d"   # dark red
    elif pct >= 150:
        return "#dc2626"   # red
    elif pct >= 100:
        return "#fca5a5"   # light red
    elif pct >= 85:
        return "#facc15"   # yellow
    elif pct >= 60:
        return "#86efac"   # light green
    elif pct >= 30:
        return "#22c55e"   # green
    else:
        return "#166534"   # dark green

def render_watchlist_group(group_name: str, watchlist: pd.DataFrame, trends: pd.DataFrame) -> None:
    """Renders graphs for data groups"""
    st.markdown(f"### {group_name}")

    group_rows = watchlist[watchlist["Group"] == group_name].copy()

    header1, header2, header3, header4 = st.columns([2.5,1,1,2])

    with header2:
        st.caption("Expended")
    with header3:
        st.caption("Budget")

    for row in group_rows.to_dict("records"):

        category_name = row["Category"]        
        category_trend = trends[trends["category"] == category_name].copy()

        spark_color = "gray"

        if len(category_trend) >= 2:
            first_val = float(category_trend["amount"].iloc[0])
            last_val = float(category_trend["amount"].iloc[-1])

            if group_name=="Income":
                if last_val > first_val:
                    spark_color = "green"
                elif last_val < first_val:
                    spark_color = "red"
                else:
                    spark_color = "gray"

            if group_name=="Expenses":
                if last_val > first_val:
                    spark_color = "red"
                elif last_val < first_val:
                    spark_color = "green"
                else:
                    spark_color = "gray"
        
        col1, col2, col3, col4 = st.columns([2.5,1,1,2])

        with col1:
            if st.button(category_name, key=f"{group_name}_{category_name}", use_container_width=True):
                st.session_state["selected_index"] = category_name
                st.success(f"Selected: {category_name}")

        with col2:
            st.write(f"${row['Amount']:,.2f}")
        
        with col3:
            pct_color = budget_pct_color(float(row["PctBudget"]))
            st.markdown(
                f"<span style='color:{pct_color}; font-weight:600;'>{row['PctBudget']:,.1f}%</span>",
                unsafe_allow_html=True
            )

        with col4:
            if len(category_trend) > 0:
                spark_data = category_trend.set_index("Month")[["amount"]].copy()
                spark_data = spark_data.reset_index(drop=True)
                spark_data["point"] = range(len(spark_data))

                spark_chart = (
                    alt.Chart(spark_data).mark_line(color=spark_color).encode(x=alt.X("point:Q", axis=None), y=alt.Y("amount:Q", axis=None)).properties(height=60)
                )
                st.altair_chart(spark_chart, use_container_width=True)
            else:
                st.write("No trend")

render_watchlist_group("Income", watchlist_df, trend_df)
render_watchlist_group("Expenses", watchlist_df, trend_df)
