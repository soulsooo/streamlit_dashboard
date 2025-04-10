import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from datetime import datetime

# Load data
@st.cache_data
def load_data():
    # You would replace this with your actual data loading code
    # For now, I'll create a mock dataframe based on your sample
    data = {
        'Номер счёта': ['750-67-8428', '226-31-3081', '631-41-3108'],
        'Филиал': ['Alex', 'Giza', 'Alex'],
        'Город': ['Yangon', 'Naypyitaw', 'Yangon'],
        'Пол': ['Female', 'Female', 'Female'],
        'Цена за единицу': [74.69, 15.28, 46.33],
        'Количество': [7, 5, 7],
        'Продажи': [548.97, 80.22, 340.53],
        'Дата': ['1/5/2019', '3/8/2019', '3/3/2019'],
        'Валовая прибыль': [26.14, 3.82, 16.22],
        'Рейтинг': [9.1, 9.6, 7.4]
    }
    return pd.DataFrame(data)

df = load_data()

# Convert date column to datetime
df['Дата'] = pd.to_datetime(df['Дата'])

# Dashboard title
st.title('Анализ продаж')

# First row - Gross Profit and Gender distribution
col1, col2 = st.columns(2)

with col1:
    total_profit = df['Валовая прибыль'].sum()
    st.metric("Сумма Валовая прибыль", f"{total_profit:,.2f} ТЫС.")

with col2:
    st.subheader("Количество Пол по Пол")
    gender_counts = df['Пол'].value_counts()
    fig = px.pie(gender_counts, 
                 values=gender_counts.values, 
                 names=gender_counts.index,
                 hole=0.3)
    st.plotly_chart(fig, use_container_width=True)

# Second row - Sales by City and Gross Profit by Date
col3, col4 = st.columns(2)

with col3:
    st.subheader("Количество Продажи по Город")
    city_counts = df['Город'].value_counts()
    fig = px.bar(city_counts, 
                 x=city_counts.index, 
                 y=city_counts.values,
                 labels={'x': 'Город', 'y': 'Количество продаж'})
    st.plotly_chart(fig, use_container_width=True)

with col4:
    st.subheader("Сумма Валовая прибыль по Дата")
    profit_by_date = df.groupby('Дата')['Валовая прибыль'].sum().reset_index()
    fig = px.line(profit_by_date, 
                  x='Дата', 
                  y='Валовая прибыль',
                  labels={'Дата': 'Дата', 'Валовая прибыль': 'Валовая прибыль'})
    st.plotly_chart(fig, use_container_width=True)

# Third row - Sales by Rating
st.subheader("Количество Продажи по Рейтинг")
rating_counts = df['Рейтинг'].value_counts().sort_index()
fig = px.bar(rating_counts, 
             x=rating_counts.index, 
             y=rating_counts.values,
             labels={'x': 'Рейтинг', 'y': 'Количество продаж'})
st.plotly_chart(fig, use_container_width=True)
