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
st.text("Hello World")