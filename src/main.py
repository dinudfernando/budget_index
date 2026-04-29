# IMPORTS
import os
import json
import pandas as pd
import numpy as np
import streamlit as st
import altair as alt


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

st.title("At a Glance...")


# Data Load
def load_transactions() -> pd.DataFrame:
    path = get_data_path("transactions.json")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"])
    df["amount"] = pd.to_numeric(df["amount"])
    return df

# Budget Load

def load_budgets() -> pd.DataFrame:
    path = get_data_path("budgets.json")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    df = pd.DataFrame(data)
    df["budget"] = pd.to_numeric(df["budget"])
    return df


transactions_df = load_transactions()
budgets_df = load_budgets()

income_mask = transactions_df["group"] == "Income"
expense_mask = transactions_df["group"] == "Expenses"

# Sample Data Metrics
total_income = transactions_df.loc[income_mask, "amount"].sum()
total_expenses = transactions_df.loc[expense_mask, "amount"].sum()
net_cashflow = total_income - total_expenses
savings_rate = (net_cashflow / total_income * 100) if total_income > 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Income", f"${total_income:,.2f}")
col2.metric("Total Expenses", f"${total_expenses:,.2f}")
col3.metric("Net Cash Flow", f"${net_cashflow:,.2f}")
col4.metric("Savings Rate", f"{savings_rate:,.2f}%")

st.divider()

#Watchlist
def build_watchlist(transactions: pd.DataFrame, budgets: pd.DataFrame) -> pd.DataFrame:
    # All transactions grouped by category and total amounts for each
    grouped = (transactions.groupby(["group", "category"], as_index=False)["amount"].sum())
    watchlist_df = pd.merge(grouped, budgets, on="category", how="left")

    watchlist_df = watchlist_df.rename(columns={
        "group": "Group",
        "category": "Category",
        "amount" : "Amount",
        "budget": "Budget"
    })

    watchlist_df["Index"] = watchlist_df["Category"] + " Index"
    #Fill nulls with 0 in budget
    watchlist_df["Budget"] = watchlist_df["Budget"].fillna(0)
    watchlist_df["Used"] = 0.0
    budget_mask = watchlist_df["Budget"] > 0
    watchlist_df.loc[budget_mask, "Used"] = (watchlist_df.loc[budget_mask, "Amount"]/ watchlist_df.loc[budget_mask, "Budget"] * 100)
    watchlist_df["Variance"] = watchlist_df["Amount"] - watchlist_df["Budget"]

    watchlist_df["Status"] = "On Track"
    watchlist_df.loc[watchlist_df["Variance"] > 0, "Status"] = "Over"
    watchlist_df.loc[watchlist_df["Variance"] < 0, "Status"] = "Under"

    # Columns in dashboard & Rounding, Sort
    watchlist_df = watchlist_df[["Group", "Index", "Amount", "Budget", "Used", "Variance", "Status"]]
    watchlist_df["Amount"] = watchlist_df["Amount"].round(2)
    watchlist_df["Budget"] = watchlist_df["Budget"].round(2)
    watchlist_df["Used"] = watchlist_df["Used"].round(1)
    watchlist_df["Variance"] = watchlist_df["Variance"].round(2)

    watchlist_df = watchlist_df.sort_values(["Group", "Index"])

    return watchlist_df

watchlist_df = build_watchlist(transactions_df, budgets_df)

# Trend Data/ sparkline

def build_trend_data(transactions: pd.DataFrame) -> pd.DataFrame:
    """Builds data for sparkline under Watchlist"""

    trend_df = transactions.copy()

    trend_df["Month"] = trend_df["date"].dt.to_period("M").astype(str)

    # Grouping transactions
    trend_df = trend_df.groupby(["category", "Month"])["amount"].sum().reset_index()


    return trend_df

trend_df = build_trend_data(transactions_df)            

def render_watchlist_group(group_name: str, watchlist: pd.DataFrame, trends: pd.DataFrame) -> None:
    """Renders graphs for data groups"""
    st.markdown(f"### {group_name}")
    group_rows = watchlist[watchlist["Group"] == group_name].copy()

    for row in group_rows.to_dict("records"):
        index_name = row["Index"]
        category_name = index_name.replace(" Index", "")

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
            if st.button(index_name, key=f"{group_name}_{index_name}", use_container_width=True):
                st.session_state["selected_index"] = index_name
                st.success(f"Selected: {index_name}")

        with col2:
            st.caption("Amount")
            st.write(f"${row["Amount"]:,.2f}")
        
        with col3:
            st.caption("Used")
            st.write(f"${row["Used"]:,.2f}")

        with col4:
            st.caption("Trend")

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

st.subheader("Watchlist")
render_watchlist_group("Income", watchlist_df, trend_df)
render_watchlist_group("Expenses", watchlist_df, trend_df)
