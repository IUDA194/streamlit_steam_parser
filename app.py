# app.py

import streamlit as st

from constants import OPTIONS
from sidebar import get_selected_option
from data_loader import load_main_csv, load_upcoming_csv
from parsers import (
    parse_followers,
    parse_price,
    parse_rating,
    parse_discount,
    parse_peak,
    parse_release_date,
)
from charts import (
    display_discount_analysis,
    display_price_vs_gain,
    display_segmentation,
    display_discount_rescue,
    display_value_analysis,
    display_over_under_rated,
    display_unexpected_hits,
    display_growth_potential,
    display_heatmap_rating_price,
    display_launch_efficiency,
)


def main():
    st.set_page_config(page_title="Steam Game Analysis", layout="wide")
    st.markdown(
        "<h1 style='text-align: center;'>🎮 Analysis of Steam game popularity and releases</h1>",
        unsafe_allow_html=True,
    )

    # Sidebar selector
    selected = get_selected_option(OPTIONS)
    st.markdown(f"### 📊 Аналітика: {selected}")

    # Load the appropriate CSV(s)
    df_main = None
    df_upcoming = None
    if selected != "Неочікувані хіти з малим фоловом":
        df_main = load_main_csv()
    else:
        df_upcoming = load_upcoming_csv()

    # Dispatch to the right analysis
    if selected == "Вплив знижки на приріст уваги":
        if df_main is not None:
            display_discount_analysis(df_main)

    elif selected == "Ціна гри vs приріст уваги":
        if df_main is not None:
            display_price_vs_gain(df_main)

    elif selected == "Сегментація за ціною та рейтингом":
        if df_main is not None:
            display_segmentation(df_main)

    elif selected == "Чи рятує знижка погані ігри":
        if df_main is not None:
            display_discount_rescue(df_main)

    elif selected == "Вигідність гри":
        if df_main is not None:
            display_value_analysis(df_main)

    elif selected == "Переоцінені й недооцінені ігри":
        if df_main is not None:
            display_over_under_rated(df_main)

    elif selected == "Неочікувані хіти з малим фоловом":
        if df_upcoming is not None:
            display_unexpected_hits(df_upcoming)

    elif selected == "Потенціал зростання гри":
        if df_main is not None:
            display_growth_potential(df_main)

    elif selected == "Нестандарт рейтинг + ціна vs онлайн":
        if df_upcoming is not None:
            display_heatmap_rating_price(df_upcoming)

    elif selected == "Ефективність запуску гри":
        if df_main is not None:
            display_launch_efficiency(df_main)

    else:
        st.error("⚠️ Оберіть валідну аналітичну категорію.")


if __name__ == "__main__":
    main()
