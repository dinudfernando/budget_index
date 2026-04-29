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

