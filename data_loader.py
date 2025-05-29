# data_loader.py

import os
import pandas as pd
import streamlit as st

# Default CSV file paths — update these to match your environment
MAIN_CSV_PATH = "/Users/aroslavgladkij/Documents/GitHub/steamdb/steamdb.csv"
UPCOMING_CSV_PATH = "/Users/aroslavgladkij/Documents/GitHub/steamdb/steamdb_upcoming.csv"

def load_main_csv(path: str = MAIN_CSV_PATH) -> pd.DataFrame | None:
    """
    Load the main Steam dataset.
    Shows a Streamlit error and returns None if the file is missing or fails to load.
    """
    if not os.path.exists(path):
        st.error(f"❌ CSV-файл не знайдено за шляхом: `{path}`")
        return None
    try:
        return pd.read_csv(path)
    except Exception as e:
        st.error(f"❌ Помилка при завантаженні `{path}`: {e}")
        return None

def load_upcoming_csv(path: str = UPCOMING_CSV_PATH) -> pd.DataFrame | None:
    """
    Load the upcoming Steam releases dataset.
    Shows a Streamlit error and returns None if the file is missing or fails to load.
    """
    if not os.path.exists(path):
        st.error(f"❌ CSV-файл не знайдено за шляхом: `{path}`")
        return None
    try:
        return pd.read_csv(path)
    except Exception as e:
        st.error(f"❌ Помилка при завантаженні `{path}`: {e}")
        return None
