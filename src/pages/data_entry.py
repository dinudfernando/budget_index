import os
import json
from datetime import date

import pandas as pd
import streamlit as st


APP_PATH = os.path.dirname(os.path.abspath(__file__))

#Path finder
def get_data_path(filename: str) -> str:
    return os.path.join(APP_PATH, "../data", filename)

