"""
Geographic View Page
Map-based visualization of weather data
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))
from src.utils.duckdb_manager import DuckDBManager

st.set_page_config(page_title="Geographic View", page_icon="🗺️", layout="wide")

st.title("🗺️ Geographic Weather View")

# Initialize DB
@st.cache_resource
def get_db():
    return DuckDBManager()

db = get_db()

# Load data with coordinates
@st.cache_data(ttl=300)
def load_geo_data():
    query = """
    WITH latest_weather AS (
        SELECT 
            city_name,
            country_code,
            latitude,
            longitude,
            temperature,
            humidity,
            wind_speed,
            weather_description,
            dt,
            ROW_NUMBER() OVER (PARTITION BY city_name ORDER BY dt DESC) as rn
        FROM raw.weather_current
    )
    SELECT * FROM latest_weather WHERE rn = 1
    """
    try:
        return db.get_dataframe(query)
    except:
        return pd.DataFrame()

st.header("Current Weather Map")

geo_data = load_geo_data()

if not geo_data.empty:
    # Map visualization
    metric_choice = st.radio(
        "Select metric to display",
        ["Temperature", "Humidity", "Wind Speed"],
        horizontal=True
    )
    
    metric_map = {
        "Temperature": "temperature",
        "Humidity": "humidity",
        "Wind Speed": "wind_speed"
    }
    
    selected_metric = metric_map[metric_choice]
    
    # Create map
    fig_map = px.scatter_mapbox(
        geo_data,
        lat="latitude",
        lon="longitude",
        size=selected_metric,
        color=selected_metric,
        hover_name="city_name",
        hover_data={
            "temperature": ":.1f",
            "humidity": True,
            "wind_speed": ":.1f",
            "weather_description": True,
            "latitude": False,
            "longitude": False
        },
        color_continuous_scale="Viridis",
        size_max=30,
        zoom=4.5,
        height=600
    )
    
    fig_map.update_layout(
        mapbox_style="open-street-map",
        margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )
    
    st.plotly_chart(fig_map, use_container_width=True)
    
    # City comparison
    st.subheader("📊 City Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_temp = px.bar(
            geo_data.sort_values('temperature', ascending=False),
            x='city_name',
            y='temperature',
            title="Temperature by City",
            labels={'city_name': 'City', 'temperature': 'Temperature (°C)'},
            color='temperature',
            color_continuous_scale='RdYlBu_r'
        )
        st.plotly_chart(fig_temp, use_container_width=True)
    
    with col2:
        fig_humidity = px.bar(
            geo_data.sort_values('humidity', ascending=False),
            x='city_name',
            y='humidity',
            title="Humidity by City",
            labels={'city_name': 'City', 'humidity': 'Humidity (%)'},
            color='humidity',
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig_humidity, use_container_width=True)
    
else:
    st.warning("No geographic data available. Please run the weather ingestion pipeline.")
