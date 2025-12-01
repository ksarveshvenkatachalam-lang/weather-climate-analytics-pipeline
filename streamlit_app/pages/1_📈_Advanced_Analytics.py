"""
Advanced Analytics Page
Detailed statistical analysis and forecasting
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))
from src.utils.duckdb_manager import DuckDBManager

st.set_page_config(page_title="Advanced Analytics", page_icon="📈", layout="wide")

st.title("📈 Advanced Weather Analytics")

# Initialize DB
@st.cache_resource
def get_db():
    return DuckDBManager()

db = get_db()

# Load data
@st.cache_data(ttl=300)
def load_historical_data(days=90):
    query = f"""
    SELECT 
        date,
        city_name,
        avg_temperature,
        min_temperature,
        max_temperature,
        avg_humidity,
        avg_wind_speed
    FROM clean.weather_daily
    WHERE date >= CURRENT_DATE - INTERVAL '{days} days'
    ORDER BY date
    """
    try:
        return db.get_dataframe(query)
    except:
        return pd.DataFrame()

st.header("🔍 Statistical Analysis")

data = load_historical_data()

if not data.empty:
    # Correlation analysis
    st.subheader("Correlation Matrix")
    
    city = st.selectbox("Select City", data['city_name'].unique())
    city_data = data[data['city_name'] == city]
    
    # Calculate correlations
    corr_cols = ['avg_temperature', 'avg_humidity', 'avg_wind_speed']
    corr_matrix = city_data[corr_cols].corr()
    
    fig_corr = px.imshow(
        corr_matrix,
        labels=dict(color="Correlation"),
        title=f"Weather Parameter Correlations - {city}",
        color_continuous_scale='RdBu',
        aspect="auto",
        text_auto='.2f'
    )
    st.plotly_chart(fig_corr, use_container_width=True)
    
    # Distribution analysis
    st.subheader("Temperature Distribution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_hist = px.histogram(
            city_data,
            x='avg_temperature',
            nbins=30,
            title=f"Temperature Distribution - {city}",
            labels={'avg_temperature': 'Temperature (°C)'}
        )
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with col2:
        fig_box = px.box(
            data,
            x='city_name',
            y='avg_temperature',
            title="Temperature Distribution by City",
            labels={'city_name': 'City', 'avg_temperature': 'Temperature (°C)'}
        )
        st.plotly_chart(fig_box, use_container_width=True)
    
    # Time series decomposition
    st.subheader("📊 Temperature Trends")
    
    # Calculate rolling averages
    city_data_sorted = city_data.sort_values('date')
    city_data_sorted['7day_ma'] = city_data_sorted['avg_temperature'].rolling(window=7).mean()
    city_data_sorted['30day_ma'] = city_data_sorted['avg_temperature'].rolling(window=30).mean()
    
    fig_ma = go.Figure()
    fig_ma.add_trace(go.Scatter(
        x=city_data_sorted['date'],
        y=city_data_sorted['avg_temperature'],
        name='Daily',
        mode='lines',
        line=dict(color='lightgray', width=1)
    ))
    fig_ma.add_trace(go.Scatter(
        x=city_data_sorted['date'],
        y=city_data_sorted['7day_ma'],
        name='7-Day Moving Average',
        mode='lines',
        line=dict(color='blue', width=2)
    ))
    fig_ma.add_trace(go.Scatter(
        x=city_data_sorted['date'],
        y=city_data_sorted['30day_ma'],
        name='30-Day Moving Average',
        mode='lines',
        line=dict(color='red', width=2)
    ))
    
    fig_ma.update_layout(
        title=f"Temperature Moving Averages - {city}",
        xaxis_title="Date",
        yaxis_title="Temperature (°C)",
        hovermode='x unified',
        height=500
    )
    st.plotly_chart(fig_ma, use_container_width=True)
    
else:
    st.warning("No data available for advanced analytics.")
