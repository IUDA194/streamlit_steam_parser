import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
import os
import numpy as np

st.set_page_config(page_title="Steam Game Analysis", layout="wide")

st.markdown("<h1 style='text-align: center;'>🎮 Analysis of Steam game popularity and releases</h1>", unsafe_allow_html=True)

# Объединённый список опций
options = [
    "Вплив знижки на приріст уваги",
    "Ціна гри vs приріст уваги",
    "Сегментація за ціною та рейтингом",
    "Чи рятує знижка погані ігри",
    "Вигідність гри",
    "Переоцінені й недооцінені ігри",
    "Неочікувані хіти з малим фоловом",
    "Потенціал зростання гри",
    "Нестандарт рейтинг + ціна vs онлайн",
    "Ефективність запуску гри"
]

# Один radio в sidebar
selected = st.sidebar.radio("🔍 Оберіть аналітичну категорію:", options)
# Центральная часть
st.markdown(f"### 📊 Аналітика: {selected}")

# Путь к CSV
csv_path = "/Users/aroslavgladkij/Documents/GitHub/steamdb/steamdb.csv"  # <-- Заміни на свій
csv_path_raiting = "/Users/aroslavgladkij/Documents/GitHub/steamdb/steamdb_upcoming.csv" 

# Только если нужная кнопка
if selected == "Вплив знижки на приріст уваги":
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        df = df.dropna(subset=["followers"])  # оставить записи с фоловерами

        # Парсим приріст фоловерів
        def parse_followers(x):
            if isinstance(x, str):
                x = re.sub(r"[^\d+]", "", x)
                if "+" in x:
                    return int(x.replace("+", ""))
                return int(x)
            return None

        # Парсим наличие скидки
        def smart_parse_discount(row):
            d = row.get("discount", "")
            if isinstance(d, str) and re.search(r"-\d+%", d):
                return True
            p = row.get("price", "")
            if isinstance(p, str) and re.search(r"-\d+%", p):
                return True
            return False

        # Применение
        df["has_discount"] = df.apply(smart_parse_discount, axis=1)
        df["followers_gain"] = df["followers"].apply(parse_followers)

        # Таблицы
        st.subheader("🎯 Ігри без знижки")
        st.dataframe(df[df["has_discount"] == False][["name", "followers_gain", "discount", "price"]].sort_values(by="followers_gain", ascending=False))

        st.subheader("💸 Ігри зі знижкою")
        st.dataframe(df[df["has_discount"] == True][["name", "followers_gain", "discount", "price"]].sort_values(by="followers_gain", ascending=False))

        # График
        q99 = df["followers_gain"].quantile(0.99)
        df_filtered = df[df["followers_gain"] < q99]

        fig, ax = plt.subplots(figsize=(8, 5))
        sns.boxplot(data=df_filtered, x="has_discount", y="followers_gain", ax=ax, palette="autumn")
        ax.set_xlabel("Є знижка")
        ax.set_ylabel("Приріст фоловерів (7 днів)")
        ax.set_title("Залежність 7d Gain від наявності знижки")
        ax.set_ylim(0, 100_000)
        ax.set_xticklabels(["False", "True"])

        st.pyplot(fig)
        
elif selected == "Ціна гри vs приріст уваги":
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        df = df.dropna(subset=["price", "followers"])

        def parse_price(x):
            if isinstance(x, str) and "€" in x:
                x = x.replace("€", "").replace(",", ".").strip()
                try:
                    return float(x)
                except:
                    return None
            elif x == "Free":
                return 0.0
            return None

        def parse_followers(x):
            if isinstance(x, str):
                x = re.sub(r"[^\d+]", "", x)
                if "+" in x:
                    return int(x.replace("+", ""))
                return int(x)
            return None

        df["price_eur"] = df["price"].apply(parse_price)
        df["followers_gain"] = df["followers"].apply(parse_followers)
        df = df.dropna(subset=["price_eur", "followers_gain"])

        # Топ-100 по приросту
        df_top = df.sort_values(by="followers_gain", ascending=False).head(100)

        # Показываем таблицу перед графиком
        st.subheader("📋 Дані для побудови графіка (топ 100)")
        st.dataframe(df_top[["name", "price", "price_eur", "followers_gain", "discount"]].reset_index(drop=True))

        # График
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.scatterplot(data=df_top, x="price_eur", y="followers_gain", ax=ax, color="orange", s=30)

        from statsmodels.nonparametric.smoothers_lowess import lowess
        lowess_smooth = lowess(df_top["followers_gain"], df_top["price_eur"], frac=0.3)
        ax.plot(lowess_smooth[:, 0], lowess_smooth[:, 1], color="black", linewidth=2)

        ax.set_xlabel("Ціна гри (€)")
        ax.set_ylabel("Приріст фоловерів")
        ax.set_title("Ціна гри vs Приріст уваги (7d Gain)")

        st.pyplot(fig)
elif selected == "Сегментація за ціною та рейтингом":
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        df = df.dropna(subset=["price", "followers", "rating"])

        def parse_price(x):
            if isinstance(x, str) and "€" in x:
                x = x.replace("€", "").replace(",", ".").strip()
                try:
                    return float(x)
                except:
                    return None
            elif x == "Free":
                return 0.0
            return None

        def parse_followers(x):
            if isinstance(x, str):
                x = re.sub(r"[^\d+]", "", x)
                if "+" in x:
                    return int(x.replace("+", ""))
                return int(x)
            return None

        def parse_rating(x):
            if isinstance(x, str) and "%" in x:
                try:
                    return float(x.replace("%", "").replace(",", "."))
                except:
                    return None
            return None

        # Применение
        df["price_eur"] = df["price"].apply(parse_price)
        df["followers_gain"] = df["followers"].apply(parse_followers)
        df["rating_pct"] = df["rating"].apply(parse_rating)
        df = df.dropna(subset=["price_eur", "followers_gain", "rating_pct"])

        # Категоризация
        def price_category(p):
            if p < 15:
                return "Low"
            elif p <= 40:
                return "Mid"
            return "High"

        def rating_category(r):
            if r >= 80:
                return "Positive"
            elif r >= 50:
                return "Mixed"
            return "Negative"

        df["price_cat"] = df["price_eur"].apply(price_category)
        df["rating_cat"] = df["rating_pct"].apply(rating_category)

        # Группировка
        pivot = df.groupby(["price_cat", "rating_cat"])["followers_gain"].mean().reset_index()
        pivot.columns = ["Ціна", "Рейтинг", "Середній 7d Gain"]

        # Таблица сбоку
        st.subheader("📋 Числові значення")
        st.dataframe(pivot.sort_values(by="Середній 7d Gain", ascending=False).reset_index(drop=True))

        # Гистограмма
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(data=pivot, x="Ціна", y="Середній 7d Gain", hue="Рейтинг", ax=ax, palette="autumn")
        ax.set_title("Середній приріст уваги (7d Gain) по категоріях ціни та рейтингу")
        st.pyplot(fig)
elif selected == "Чи рятує знижка погані ігри":
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        df = df.dropna(subset=["followers", "rating"])

        def parse_followers(x):
            if isinstance(x, str):
                x = re.sub(r"[^\d+]", "", x)
                if "+" in x:
                    return int(x.replace("+", ""))
                return int(x)
            return None

        def parse_rating(x):
            if isinstance(x, str) and "%" in x:
                try:
                    return float(x.replace("%", "").replace(",", "."))
                except:
                    return None
            return None

        def parse_discount(x):
            if isinstance(x, str) and re.search(r"-\d+%", x):
                return True
            return False

        # Применение
        df["followers_gain"] = df["followers"].apply(parse_followers)
        df["rating_pct"] = df["rating"].apply(parse_rating)
        df["has_discount"] = df["discount"].apply(parse_discount)
        df = df.dropna(subset=["followers_gain", "rating_pct"])

        # Фильтруем плохие игры
        bad_games = df[df["rating_pct"] < 50]

        # Топ-100 по приросту
        top_bad = bad_games.sort_values(by="followers_gain", ascending=False).head(100)

        # Таблиця
        st.subheader("📋 Дані для побудови графіка")
        st.dataframe(top_bad[["name", "followers_gain", "rating", "discount"]].reset_index(drop=True))

        # График
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.boxplot(data=top_bad, x="has_discount", y="followers_gain", ax=ax, palette="autumn")
        ax.set_xlabel("Є знижка")
        ax.set_ylabel("7d Gain")
        ax.set_title("Знижка для ігор з поганим рейтингом")
        ax.set_xticklabels(["False", "True"])
        ax.set_ylim(0, 20000)

        st.pyplot(fig)

elif selected == "Вигідність гри":
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        df = df.dropna(subset=["price", "followers"])

        def parse_price(x):
            if isinstance(x, str):
                if "€" in x:
                    x = x.replace("€", "").replace(",", ".").strip()
                    try:
                        return float(x)
                    except:
                        return None
                elif x == "Free":
                    return 0.0
            return None

        def parse_followers(x):
            if isinstance(x, str):
                x = re.sub(r"[^\d+]", "", x)
                if "+" in x:
                    return int(x.replace("+", ""))
                return int(x)
            return None

        # Применяем
        df["price_eur"] = df["price"].apply(parse_price)
        df["followers_gain"] = df["followers"].apply(parse_followers)
        df = df.dropna(subset=["price_eur", "followers_gain"])
        df = df[df["price_eur"] > 0]

        # Выгодность
        df["value_score"] = df["followers_gain"] / df["price_eur"]

        # Топ-100 по выгодности
        top_value = df.sort_values(by="value_score", ascending=False).head(100)
        top10 = top_value.head(10)


        # Таблица
        st.subheader("📋 Дані найвигідніших ігор")
        st.dataframe(top10[["name", "followers_gain", "price_eur", "value_score"]].reset_index(drop=True))


        # Горизонтальный barplot
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.barplot(data=top10, y="name", x="value_score", palette="pastel", ax=ax)
        ax.set_title("Топ-10 найвигідніших ігор (7d Gain / Price)")
        ax.set_xlabel("Інтерес за 1 євро")
        ax.set_ylabel("Назва гри")

        st.pyplot(fig)
elif selected == "Переоцінені й недооцінені ігри":
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        df = df.dropna(subset=["followers", "rating"])

        def parse_followers(x):
            if isinstance(x, str):
                x = re.sub(r"[^\d+]", "", x)
                if "+" in x:
                    return int(x.replace("+", ""))
                return int(x)
            return None

        def parse_rating(x):
            if isinstance(x, str) and "%" in x:
                try:
                    return float(x.replace("%", "").replace(",", "."))
                except:
                    return None
            return None

        # Применение
        df["followers_gain"] = df["followers"].apply(parse_followers)
        df["rating_pct"] = df["rating"].apply(parse_rating)
        df = df.dropna(subset=["followers_gain", "rating_pct"])
        df = df[df["rating_pct"] > 0]  # убрать деление на 0

        # value_index = followers / рейтинг
        df["value_index"] = df["followers_gain"] / df["rating_pct"]

        # Переоцінені = рейтинг високий, приріст малий
        overrated = df.sort_values(by="value_index", ascending=True).head(5)

        # Недооціненні = рейтинг низький, приріст високий
        underrated = df.sort_values(by="value_index", ascending=False).head(5)
        
        # Таблицы
        st.subheader("📋 Переоцінені ігри")
        st.dataframe(overrated[["name", "followers_gain", "rating_pct", "value_index"]].reset_index(drop=True))

        st.subheader("📋 Недооцінені ігри")
        st.dataframe(underrated[["name", "followers_gain", "rating_pct", "value_index"]].reset_index(drop=True))

        # Два графика
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        sns.barplot(data=overrated, x="value_index", y="name", ax=ax1, palette="autumn")
        ax1.set_title("Переоцінені ігри")
        ax1.set_xlabel("value_index")
        ax1.set_ylabel("Name")

        sns.barplot(data=underrated, x="value_index", y="name", ax=ax2, palette="spring")
        ax2.set_title("Недооцінені ігри")
        ax2.set_xlabel("value_index")
        ax2.set_ylabel("")

        st.pyplot(fig)
elif selected == "Неочікувані хіти з малим фоловом":
    if os.path.exists(csv_path_raiting):
        df = pd.read_csv(csv_path_raiting)
        df = df.dropna(subset=["price", "followers", "owners"])  # в owners мы берём peak

        def parse_price(x):
            if isinstance(x, str):
                if "€" in x:
                    x = x.replace("€", "").replace(",", ".").strip()
                    try:
                        return float(x)
                    except:
                        return None
                elif x == "Free":
                    return 0.0
            return None

        def parse_followers(x):
            if isinstance(x, str):
                digits = re.sub(r"[^\d]", "", x)
                if digits:
                    return int(digits)
            return None

        def parse_peak(x):
            if isinstance(x, str):
                digits = re.sub(r"[^\d]", "", x)
                if digits:
                    return int(digits)
            return None

        df["price_eur"] = df["price"].apply(parse_price)
        df["followers_num"] = df["followers"].apply(parse_followers)
        df["peak_num"] = df["owners"].apply(parse_peak)  # здесь peak онлайн
        df = df.dropna(subset=["price_eur", "followers_num", "peak_num"])
        df = df[(df["followers_num"] > 0) & (df["price_eur"] > 0)]

        # KPI = peak / followers (или наоборот)
        df["peak_ratio"] = df["peak_num"] / df["followers_num"]

        # Обрезаем
        top_under = df.sort_values(by="peak_ratio", ascending=False).head(5)
        top_over = df.sort_values(by="peak_ratio", ascending=True).head(5)


        # Таблицы
        st.subheader("📋 Переоцінені ігри")
        st.dataframe(top_over[["name", "followers_num", "peak_num", "peak_ratio"]].reset_index(drop=True))

        st.subheader("📋 Неочікувані хіти")
        st.dataframe(top_under[["name", "followers_num", "peak_num", "peak_ratio"]].reset_index(drop=True))


        # Два графика
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        sns.barplot(data=top_over, x="peak_ratio", y="name", ax=ax1, palette="Reds")
        ax1.set_title("Переоцінені ігри")
        ax1.set_xlabel("Peak / Followers")

        sns.barplot(data=top_under, x="peak_ratio", y="name", ax=ax2, palette="Greens")
        ax2.set_title("Недооцінені ігри")
        ax2.set_xlabel("Peak / Followers")

        st.pyplot(fig)
        
elif selected == "Потенціал зростання гри":
    if os.path.exists(csv_path):
        import datetime

        df = pd.read_csv(csv_path)
        df = df.dropna(subset=["followers", "release_date"])

        def parse_followers(x):
            if isinstance(x, str):
                x = re.sub(r"[^\d+]", "", x)
                if "+" in x:
                    return int(x.replace("+", ""))
                return int(x)
            return None

        def parse_release_date(x):
            try:
                return pd.to_datetime(x)
            except:
                return None

        # Текущая дата
        today = pd.to_datetime("today")

        df["followers_num"] = df["followers"].apply(parse_followers)
        df["release_date_parsed"] = df["release_date"].apply(parse_release_date)
        df["days_since_release"] = (today - df["release_date_parsed"]).dt.days
        df = df.dropna(subset=["followers_num", "days_since_release"])
        df = df[df["days_since_release"] > 0]

        # Индекс запуску
        df["launch_index"] = df["followers_num"] / df["days_since_release"]

        # Топ-100 по launch_index
        top_launch = df.sort_values(by="launch_index", ascending=False).head(10)

        # График
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.barplot(data=top_launch, x="launch_index", y="name", palette="Blues", ax=ax)
        ax.set_title("Топ-10 запусків за ефективністю")
        ax.set_xlabel("Індекс запуску")
        ax.set_ylabel("Назва гри")

        st.pyplot(fig)

        # Таблица
        st.subheader("📋 Дані запусків")
        st.dataframe(top_launch[["name", "followers_num", "release_date", "days_since_release", "launch_index"]].reset_index(drop=True))
        
elif selected == "Нестандарт рейтинг + ціна vs онлайн":
    if os.path.exists(csv_path_raiting):
        df = pd.read_csv(csv_path_raiting)
        df = df.dropna(subset=["price", "rating", "owners"])

        def parse_price(x):
            if isinstance(x, str):
                if "€" in x:
                    x = x.replace("€", "").replace(",", ".").strip()
                    try:
                        return float(x)
                    except:
                        return None
                elif x == "Free":
                    return 0.0
            return None

        def parse_rating(x):
            if isinstance(x, str) and "%" in x:
                try:
                    return float(x.replace("%", "").replace(",", "."))
                except:
                    return None
            return None

        def parse_peak(x):
            if isinstance(x, str):
                digits = re.sub(r"[^\d]", "", x)
                if digits:
                    return int(digits)
            return None


        df["price_eur"] = df["price"].apply(parse_price)
        df["rating_pct"] = df["rating"].apply(parse_rating)
        df["peak"] = df["owners"].apply(parse_peak)

        df = df.dropna(subset=["price_eur", "rating_pct", "peak"])

        def price_category(p):
            if p < 15:
                return "Low"
            elif p <= 40:
                return "Mid"
            return "High"

        def rating_category(r):
            if r >= 80:
                return "Positive"
            elif r >= 50:
                return "Mixed"
            return "Negative"

        df["price_cat"] = df["price_eur"].apply(price_category)
        df["rating_cat"] = df["rating_pct"].apply(rating_category)
        
        pivot = df.pivot_table(index="rating_cat", columns="price_cat", values="peak", aggfunc="mean")
        
        if not pivot.empty:
            fig, ax = plt.subplots(figsize=(8, 5))
            st.subheader("📋 Зведена таблиця")
            st.dataframe(pivot.reset_index())
            sns.heatmap(pivot, annot=True, fmt=".0f", cmap="Blues", ax=ax)
            ax.set_title("Середній пік онлайну: рейтинг + ціна")
            st.pyplot(fig)
        else:
            st.warning("⚠️ Недостатньо даних для побудови теплової карти.")
elif selected == "Ефективність запуску гри":
    if os.path.exists(csv_path):
        import datetime

        df = pd.read_csv(csv_path)
        df = df.dropna(subset=["followers", "release_date"])

        def parse_followers(x):
            if isinstance(x, str):
                digits = re.sub(r"[^\d]", "", x)
                if digits:
                    return int(digits)
            return None

        def parse_release_date(x):
            try:
                return pd.to_datetime(x)
            except:
                return None

        today = pd.to_datetime("today")

        df["followers_num"] = df["followers"].apply(parse_followers)
        df["release_date_parsed"] = df["release_date"].apply(parse_release_date)
        df["days_since_release"] = (today - df["release_date_parsed"]).dt.days

        df = df.dropna(subset=["followers_num", "days_since_release"])
        df = df[df["days_since_release"] > 0]

        df["launch_index"] = df["followers_num"] / df["days_since_release"]

        top_launch = df.sort_values(by="launch_index", ascending=False).head(10)

        # Таблица
        st.subheader("📋 Деталі запуску (топ-10)")
        st.dataframe(top_launch[["name", "followers_num", "release_date", "days_since_release", "launch_index"]].reset_index(drop=True))


        # График
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.barplot(data=top_launch, x="launch_index", y="name", palette="pastel", ax=ax)
        ax.set_title("Топ-10 запусків за ефективністю")
        ax.set_xlabel("Індекс запуску")
        ax.set_ylabel("Назва гри")

        st.pyplot(fig)



    else:
        st.error(f"❌ CSV-файл не знайдено за шляхом: `{csv_path}`")
