# IMPORTS
import os
import json
import pandas as pd
import numpy as np
import streamlit as st


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
    trend_df = transactions.copy()

    trend_df["Month"] = trend_df["date"].dt.to_period("M").astype(str)

    return trend_df

st.subheader("Watchlist")

st.dataframe(
    watchlist_df, 
    use_container_width=True, 
    hide_index=True, 
    column_config={
        "Amount": st.column_config.NumberColumn("Amount", format="$%.2f"),
        "Budget": st.column_config.NumberColumn("Budget", format="$%.2f"),
        "Used": st.column_config.NumberColumn("Used", format="%.1f%%"),
        "Variance": st.column_config.NumberColumn("Variance", format="$ %.2f"),
    }
    )