import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime

# Настройка страницы
st.set_page_config(
    layout="wide",
    page_title="🌦 Погодный дашборд",
    page_icon="🌍"
)

# Заголовок
st.title("🌍 Анализ погоды по городам")
st.markdown("---")

# 1. Словарь городов с координатами
CITIES = {
    "Москва": {"lat": 55.7558, "lon": 37.6176},
    "Новосибирск": {"lat": 55.0084, "lon": 82.9357},
    "Сочи": {"lat": 43.5855, "lon": 39.7231},
    "Астрахань": {"lat": 46.3477, "lon": 48.0305}
}

# 2. Настройки в сайдбаре
with st.sidebar:
    st.header("⚙️ Настройки")
    selected_cities = st.multiselect(
        "Выберите города",
        list(CITIES.keys()),
        default=["Москва", "Сочи"]
    )
    
    year = st.slider("Год анализа", 2021, 2022, 2023, 2024)
    date_start = datetime(year, 1, 1)
    date_end = datetime(year, 12, 31)
    
    st.markdown("---")
    st.info("Данные загружаются с Open-Meteo API")

# 3. Загрузка данных с кэшированием
@st.cache_data
def load_weather_data(cities, date_start, date_end):
    all_data = []
    
    for city_name, coords in cities.items():
        url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": coords["lat"],
            "longitude": coords["lon"],
            "start_date": date_start.strftime("%Y-%m-%d"),
            "end_date": date_end.strftime("%Y-%m-%d"),
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
            "timezone": "auto"
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data["daily"])
            df["date"] = pd.to_datetime(df["time"])
            df["city"] = city_name
            all_data.append(df)
    
    return pd.concat(all_data) if all_data else None

weather_df = load_weather_data(
    {city: CITIES[city] for city in selected_cities},
    date_start,
    date_end
)

if weather_df is None:
    st.error("Не удалось загрузить данные. Попробуйте позже.")
    st.stop()

# 4. Основные метрики
st.subheader("📊 Ключевые показатели")
cols = st.columns(3)
with cols[0]:
    st.metric("Городов в анализе", len(selected_cities))
with cols[1]:
    st.metric("Средняя макс. температура", 
             f"{weather_df['temperature_2m_max'].mean():.1f}°C")
with cols[2]:
    st.metric("Средняя сумма осадков", 
             f"{weather_df['precipitation_sum'].mean():.1f} мм")

st.markdown("---")

# 5. Визуализация данных
tab1, tab2, tab3 = st.tabs(["Температура", "Осадки", "Детали по городу"])

with tab1:
    st.subheader("🌡️ Динамика температур")
    fig_temp = px.line(
        weather_df,
        x="date",
        y=["temperature_2m_max", "temperature_2m_min"],
        color="city",
        title=f"Температура по городам ({year})",
        labels={"value": "Температура (°C)"}
    )
    st.plotly_chart(fig_temp, use_container_width=True)

with tab2:
    st.subheader("🌧️ Осадки")
    fig_precip = px.bar(
        weather_df,
        x="date",
        y="precipitation_sum",
        color="city",
        title=f"Сумма осадков по городам ({year})",
        labels={"precipitation_sum": "Осадки (мм)"}
    )
    st.plotly_chart(fig_precip, use_container_width=True)

with tab3:
    st.subheader("🔍 Детальный анализ по городу")
    city = st.selectbox("Выберите город", selected_cities)
    
    city_data = weather_df[weather_df["city"] == city]
    
    # График температур
    fig_city_temp = px.bar(
        city_data,
        x="date",
        y=["temperature_2m_max", "temperature_2m_min"],
        title=f"Температура в {city} ({year})",
        barmode="group",
        labels={"value": "Температура (°C)"}
    )
    st.plotly_chart(fig_city_temp, use_container_width=True)
    
    # Анализ по месяцам
    city_data["month"] = city_data["date"].dt.month_name()
    monthly_stats = city_data.groupby("month").agg({
        "temperature_2m_max": "mean",
        "temperature_2m_min": "mean",
        "precipitation_sum": "sum"
    }).reset_index()
    
    cols = st.columns(2)
    with cols[0]:
        st.markdown("**Средняя температура по месяцам**")
        fig_month = px.line(
            monthly_stats,
            x="month",
            y=["temperature_2m_max", "temperature_2m_min"],
            labels={"value": "Температура (°C)"}
        )
        st.plotly_chart(fig_month, use_container_width=True)
    
    with cols[1]:
        st.markdown("**Осадки по месяцам**")
        fig_month_precip = px.bar(
            monthly_stats,
            x="month",
            y="precipitation_sum",
            labels={"precipitation_sum": "Осадки (мм)"}
        )
        st.plotly_chart(fig_month_precip, use_container_width=True)



# Подвал
st.markdown("---")
st.caption("Данные предоставлены Open-Meteo API")
