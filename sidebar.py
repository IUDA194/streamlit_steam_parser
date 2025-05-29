import streamlit as st
from constants import OPTIONS

def select_category():
    return st.sidebar.radio("🔍 Оберіть аналітичну категорію:", OPTIONS)

def get_selected_option(options, label="🔍 Оберіть аналітичну категорію:"):
    """
    Render a radio selection in the sidebar and return the selected value.

    Parameters:
    - options: list of str, the choices to display
    - label: str, the label to show above the radio buttons

    Returns:
    - selected option (str)
    """
    return st.sidebar.radio(label, options)