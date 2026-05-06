import os
import json
from datetime import date

import pandas as pd
import streamlit as st

APP_PATH = os.path.dirname(os.path.abspath(__file__))

#Path finder
def get_data_path(filename: str) -> str:
    return os.path.join(APP_PATH, "../data", filename)

st.set_page_config(
    page_title="New Data Entry",
    page_icon="🗳️",
    layout="wide"
)

#Load current transaction list
@st.cache_data
def load_transactions() -> pd.DataFrame:
    path = get_data_path("transactions.json")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"])
    df["amount"] = pd.to_numeric(df["amount"])
    return df

# Save new records to transactions file
def save_transaction(record: dict) -> None:
    path = get_data_path("transactions.json")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    data.append(record)

    data = sorted(data, key=lambda x: x["date"])

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    load_transactions.clear()


transactions_df = load_transactions()

income_categories = sorted(
    transactions_df.loc[transactions_df["group"] == "Income", "category"].dropna().unique().tolist()
)

expenses_categories = sorted(
    transactions_df.loc[transactions_df["group"] == "Expenses", "category"].dropna().unique().tolist()
)

st.title("New Data Entry")
st.caption("Add a new transaction under income or expenses")

group = st.selectbox(
    "Group",
    ["Income", "Expenses"],
    key="entry_group"
)

if group=="Income":
    category_options = income_categories
else:
    category_options = expenses_categories

if "entry_category" in st.session_state and st.session_state["entry_category"] not in category_options:
    st.session_state["entry_category"] = category_options[0]

category = st.selectbox("Category", category_options, key="entry_category")


with st.form("new_transaction_form"):
    entry_date = st.date_input("Date", value=date.today())
    amount = st.number_input("Amount", min_value=0.0, step=1.0, format="%.2f")
    tag = st.text_input("Tag", placeholder="Groceries, Rent, Paycheck etc..")

    submitted = st.form_submit_button("Save Record", use_container_width=True)

if submitted:
    if amount <= 0:
        st.error("Amount must be greater than 0!")
    elif not tag.strip():
        st.error("Tag is required.")
    else:
        new_record = {
            "date": entry_date.strftime("%Y-%m-%d"),
            "group": group,
            "category": category,
            "amount": round(float(amount), 2),
            "tag": tag.strip()
        }
        save_transaction(new_record)
        st.success("New record saved successfully!")
        st.json(new_record)