# charts.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.nonparametric.smoothers_lowess import lowess

from parsers import (
    parse_followers,
    parse_price,
    parse_rating,
    parse_discount,
    parse_peak,
    parse_release_date,
)


def display_discount_analysis(df: pd.DataFrame):
    df = df.dropna(subset=["followers"])
    df["has_discount"] = df.apply(lambda row: parse_discount(row.get("discount", "")) or parse_discount(row.get("price", "")), axis=1)
    df["followers_gain"] = df["followers"].apply(parse_followers)

    st.subheader("🎯 Ігри без знижки")
    st.dataframe(
        df[df["has_discount"] == False][
            ["name", "followers_gain", "discount", "price"]
        ].sort_values("followers_gain", ascending=False)
    )

    st.subheader("💸 Ігри зі знижкою")
    st.dataframe(
        df[df["has_discount"] == True][
            ["name", "followers_gain", "discount", "price"]
        ].sort_values("followers_gain", ascending=False)
    )

    # Boxplot without extreme outliers
    q99 = df["followers_gain"].quantile(0.99)
    filtered = df[df["followers_gain"] < q99]

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.boxplot(
        data=filtered,
        x="has_discount",
        y="followers_gain",
        ax=ax,
        palette="autumn"
    )
    ax.set_xlabel("Є знижка")
    ax.set_ylabel("Приріст фоловерів (7 днів)")
    ax.set_title("Залежність 7d Gain від наявності знижки")
    ax.set_ylim(0, 100_000)
    ax.set_xticklabels(["False", "True"])
    st.pyplot(fig)


def display_price_vs_gain(df: pd.DataFrame):
    df = df.dropna(subset=["price", "followers"])
    df["price_eur"] = df["price"].apply(parse_price)
    df["followers_gain"] = df["followers"].apply(parse_followers)
    df = df.dropna(subset=["price_eur", "followers_gain"])

    df_top = df.sort_values("followers_gain", ascending=False).head(100)
    st.subheader("📋 Дані для побудови графіка (топ 100)")
    st.dataframe(
        df_top[["name", "price", "price_eur", "followers_gain", "discount"]]
        .reset_index(drop=True)
    )

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.scatterplot(
        data=df_top,
        x="price_eur",
        y="followers_gain",
        ax=ax,
        s=30
    )
    smooth = lowess(df_top["followers_gain"], df_top["price_eur"], frac=0.3)
    ax.plot(smooth[:, 0], smooth[:, 1], color="black", linewidth=2)
    ax.set_xlabel("Ціна гри (€)")
    ax.set_ylabel("Приріст фоловерів")
    ax.set_title("Ціна гри vs Приріст уваги (7d Gain)")
    st.pyplot(fig)


def display_segmentation(df: pd.DataFrame):
    df = df.dropna(subset=["price", "followers", "rating"])
    df["price_eur"] = df["price"].apply(parse_price)
    df["followers_gain"] = df["followers"].apply(parse_followers)
    df["rating_pct"] = df["rating"].apply(parse_rating)
    df = df.dropna(subset=["price_eur", "followers_gain", "rating_pct"])

    def price_cat(p):
        if p < 15: return "Low"
        if p <= 40: return "Mid"
        return "High"

    def rating_cat(r):
        if r >= 80: return "Positive"
        if r >= 50: return "Mixed"
        return "Negative"

    df["price_cat"] = df["price_eur"].apply(price_cat)
    df["rating_cat"] = df["rating_pct"].apply(rating_cat)

    pivot = (
        df.groupby(["price_cat", "rating_cat"])["followers_gain"]
        .mean()
        .reset_index()
        .rename(columns={"followers_gain": "Середній 7d Gain", "price_cat": "Ціна", "rating_cat": "Рейтинг"})
    )

    st.subheader("📋 Числові значення")
    st.dataframe(pivot.sort_values("Середній 7d Gain", ascending=False).reset_index(drop=True))

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(
        data=pivot,
        x="Ціна",
        y="Середній 7d Gain",
        hue="Рейтинг",
        ax=ax,
        palette="autumn"
    )
    ax.set_title("Середній приріст уваги (7d Gain) по категоріях ціни та рейтингу")
    st.pyplot(fig)


def display_discount_rescue(df: pd.DataFrame):
    df = df.dropna(subset=["followers", "rating"])
    df["followers_gain"] = df["followers"].apply(parse_followers)
    df["rating_pct"] = df["rating"].apply(parse_rating)
    df["has_discount"] = df["discount"].apply(parse_discount)
    df = df.dropna(subset=["followers_gain", "rating_pct"])

    bad = df[df["rating_pct"] < 50]
    top_bad = bad.sort_values("followers_gain", ascending=False).head(100)

    st.subheader("📋 Дані для побудови графіка")
    st.dataframe(
        top_bad[["name", "followers_gain", "rating", "discount"]]
        .reset_index(drop=True)
    )

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.boxplot(
        data=top_bad,
        x="has_discount",
        y="followers_gain",
        ax=ax,
        palette="autumn"
    )
    ax.set_xlabel("Є знижка")
    ax.set_ylabel("7d Gain")
    ax.set_title("Знижка для ігор з поганим рейтингом")
    ax.set_xticklabels(["False", "True"])
    ax.set_ylim(0, 20_000)
    st.pyplot(fig)


def display_value_analysis(df: pd.DataFrame):
    df = df.dropna(subset=["price", "followers"])
    df["price_eur"] = df["price"].apply(parse_price)
    df["followers_gain"] = df["followers"].apply(parse_followers)
    df = df.dropna(subset=["price_eur", "followers_gain"])
    df = df[df["price_eur"] > 0]

    df["value_score"] = df["followers_gain"] / df["price_eur"]
    top10 = df.sort_values("value_score", ascending=False).head(10)

    st.subheader("📋 Дані найвигідніших ігор")
    st.dataframe(
        top10[["name", "followers_gain", "price_eur", "value_score"]]
        .reset_index(drop=True)
    )

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(
        data=top10,
        y="name",
        x="value_score",
        ax=ax
    )
    ax.set_title("Топ-10 найвигідніших ігор (7d Gain / Price)")
    ax.set_xlabel("Інтерес за 1 євро")
    ax.set_ylabel("Назва гри")
    st.pyplot(fig)


def display_over_under_rated(df: pd.DataFrame):
    df = df.dropna(subset=["followers", "rating"])
    df["followers_gain"] = df["followers"].apply(parse_followers)
    df["rating_pct"] = df["rating"].apply(parse_rating)
    df = df.dropna(subset=["followers_gain", "rating_pct"])
    df = df[df["rating_pct"] > 0]

    df["value_index"] = df["followers_gain"] / df["rating_pct"]
    overrated = df.sort_values("value_index", ascending=True).head(5)
    underrated = df.sort_values("value_index", ascending=False).head(5)

    st.subheader("📋 Переоцінені ігри")
    st.dataframe(
        overrated[["name", "followers_gain", "rating_pct", "value_index"]]
        .reset_index(drop=True)
    )

    st.subheader("📋 Недооцінені ігри")
    st.dataframe(
        underrated[["name", "followers_gain", "rating_pct", "value_index"]]
        .reset_index(drop=True)
    )

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    sns.barplot(data=overrated, x="value_index", y="name", ax=ax1, palette="autumn")
    ax1.set_title("Переоцінені ігри")
    ax1.set_xlabel("value_index")
    ax1.set_ylabel("Name")

    sns.barplot(data=underrated, x="value_index", y="name", ax=ax2, palette="spring")
    ax2.set_title("Недооцінені ігри")
    ax2.set_xlabel("value_index")
    st.pyplot(fig)


def display_unexpected_hits(df: pd.DataFrame):
    df = df.dropna(subset=["price", "followers", "owners"])
    df["price_eur"] = df["price"].apply(parse_price)
    df["followers_num"] = df["followers"].apply(parse_followers)
    df["peak_num"] = df["owners"].apply(parse_peak)
    df = df.dropna(subset=["price_eur", "followers_num", "peak_num"])
    df = df[(df["followers_num"] > 0) & (df["price_eur"] > 0)]

    df["peak_ratio"] = df["peak_num"] / df["followers_num"]
    top_under = df.sort_values("peak_ratio", ascending=False).head(5)
    top_over = df.sort_values("peak_ratio", ascending=True).head(5)

    st.subheader("📋 Переоцінені ігри")
    st.dataframe(
        top_over[["name", "followers_num", "peak_num", "peak_ratio"]]
        .reset_index(drop=True)
    )

    st.subheader("📋 Неочікувані хіти")
    st.dataframe(
        top_under[["name", "followers_num", "peak_num", "peak_ratio"]]
        .reset_index(drop=True)
    )

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    sns.barplot(data=top_over, x="peak_ratio", y="name", ax=ax1)
    ax1.set_title("Переоцінені ігри")
    ax1.set_xlabel("Peak / Followers")

    sns.barplot(data=top_under, x="peak_ratio", y="name", ax=ax2)
    ax2.set_title("Недооцінені ігри")
    ax2.set_xlabel("Peak / Followers")
    st.pyplot(fig)


def display_growth_potential(df: pd.DataFrame):
    df = df.dropna(subset=["followers", "release_date"])
    today = pd.to_datetime("today")
    df["followers_num"] = df["followers"].apply(parse_followers)
    df["release_date_parsed"] = df["release_date"].apply(parse_release_date)
    df["days_since_release"] = (today - df["release_date_parsed"]).dt.days
    df = df.dropna(subset=["followers_num", "days_since_release"])
    df = df[df["days_since_release"] > 0]

    df["launch_index"] = df["followers_num"] / df["days_since_release"]
    top_launch = df.sort_values("launch_index", ascending=False).head(10)

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(data=top_launch, x="launch_index", y="name", ax=ax)
    ax.set_title("Топ-10 запусків за ефективністю")
    ax.set_xlabel("Індекс запуску")
    ax.set_ylabel("Назва гри")
    st.pyplot(fig)

    st.subheader("📋 Дані запусків")
    st.dataframe(
        top_launch[
            ["name", "followers_num", "release_date", "days_since_release", "launch_index"]
        ].reset_index(drop=True)
    )


def display_heatmap_rating_price(df: pd.DataFrame):
    df = df.dropna(subset=["price", "rating", "owners"])
    df["price_eur"] = df["price"].apply(parse_price)
    df["rating_pct"] = df["rating"].apply(parse_rating)
    df["peak"] = df["owners"].apply(parse_peak)
    df = df.dropna(subset=["price_eur", "rating_pct", "peak"])

    def price_cat(p):
        if p < 15: return "Low"
        if p <= 40: return "Mid"
        return "High"

    def rating_cat(r):
        if r >= 80: return "Positive"
        if r >= 50: return "Mixed"
        return "Negative"

    df["price_cat"] = df["price_eur"].apply(price_cat)
    df["rating_cat"] = df["rating_pct"].apply(rating_cat)

    pivot = df.pivot_table(
        index="rating_cat",
        columns="price_cat",
        values="peak",
        aggfunc="mean"
    )

    if pivot.empty:
        st.warning("⚠️ Недостатньо даних для побудови теплової карти.")
        return

    st.subheader("📋 Зведена таблиця")
    st.dataframe(pivot.reset_index())

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.heatmap(pivot, annot=True, fmt=".0f", cmap="Blues", ax=ax)
    ax.set_title("Середній пік онлайну: рейтинг + ціна")
    st.pyplot(fig)


def display_launch_efficiency(df: pd.DataFrame):
    df = df.dropna(subset=["followers", "release_date"])
    today = pd.to_datetime("today")
    df["followers_num"] = df["followers"].apply(parse_followers)
    df["release_date_parsed"] = df["release_date"].apply(parse_release_date)
    df["days_since_release"] = (today - df["release_date_parsed"]).dt.days
    df = df.dropna(subset=["followers_num", "days_since_release"])
    df = df[df["days_since_release"] > 0]

    df["launch_index"] = df["followers_num"] / df["days_since_release"]
    top_launch = df.sort_values("launch_index", ascending=False).head(10)

    st.subheader("📋 Деталі запуску (топ-10)")
    st.dataframe(
        top_launch[
            ["name", "followers_num", "release_date", "days_since_release", "launch_index"]
        ].reset_index(drop=True)
    )

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(data=top_launch, x="launch_index", y="name", ax=ax)
    ax.set_title("Топ-10 запусків за ефективністю")
    ax.set_xlabel("Індекс запуску")
    ax.set_ylabel("Назва гри")
    st.pyplot(fig)
