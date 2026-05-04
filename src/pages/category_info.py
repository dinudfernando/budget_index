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