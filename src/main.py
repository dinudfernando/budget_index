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
expense_mask = transactions_df["group"] == "Expense"

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

st.divider