"""
Weather & Climate Analytics Dashboard
Built with Streamlit
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

from src.utils.duckdb_manager import DuckDBManager

# Page configuration
st.set_page_config(
    page_title="Weather Analytics Dashboard",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# Initialize database connection
@st.cache_resource
def get_db_connection():
    return DuckDBManager()

db = get_db_connection()

# Data loading functions
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_current_weather():
    """Load latest weather data for all cities"""
    query = """
    WITH latest_weather AS (
        SELECT 
            city_name,
            country_code,
            temperature,
            feels_like,
            humidity,
            pressure,
            wind_speed,
            weather_main,
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

@st.cache_data(ttl=300)
def load_daily_weather(days=30):
    """Load daily weather summaries"""
    query = f"""
    SELECT 
        date,
        city_name,
        avg_temperature,
        min_temperature,
        max_temperature,
        avg_humidity,
        avg_pressure,
        avg_wind_speed,
        weather_condition
    FROM clean.weather_daily
    WHERE date >= CURRENT_DATE - INTERVAL '{days} days'
    ORDER BY date DESC, city_name
    """
    try:
        return db.get_dataframe(query)
    except:
        return pd.DataFrame()

@st.cache_data(ttl=300)
def load_temperature_trends():
    """Load temperature trends analytics"""
    query = """
    SELECT 
        city_name,
        year,
        month,
        avg_temperature,
        min_temperature,
        max_temperature,
        temperature_variance,
        days_above_avg,
        days_below_avg
    FROM analytics.temperature_trends
    ORDER BY year DESC, month DESC
    """
    try:
        return db.get_dataframe(query)
    except:
        return pd.DataFrame()

@st.cache_data(ttl=300)
def load_weather_patterns():
    """Load weather pattern analytics"""
    query = """
    SELECT 
        city_name,
        month,
        weather_condition,
        frequency,
        avg_temperature,
        avg_precipitation
    FROM analytics.weather_patterns
    ORDER BY city_name, month
    """
    try:
        return db.get_dataframe(query)
    except:
        return pd.DataFrame()

@st.cache_data(ttl=300)
def load_forecast_data():
    """Load forecast data"""
    query = """
    SELECT 
        city_name,
        forecast_time,
        temperature,
        weather_main,
        weather_description,
        pop as precipitation_probability,
        wind_speed
    FROM raw.weather_forecast
    WHERE forecast_time >= CURRENT_TIMESTAMP
    ORDER BY city_name, forecast_time
    LIMIT 200
    """
    try:
        return db.get_dataframe(query)
    except:
        return pd.DataFrame()

# Header
st.markdown('<h1 class="main-header">🌤️ Weather & Climate Analytics</h1>', unsafe_allow_html=True)
st.markdown("### Real-time weather data pipeline with multi-source API integration")

# Sidebar
with st.sidebar:
    st.header("⚙️ Dashboard Settings")
    
    # Refresh button
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    st.divider()
    
    # Time range selector
    time_range = st.selectbox(
        "Historical Data Range",
        [7, 14, 30, 60, 90],
        index=2,
        format_func=lambda x: f"Last {x} days"
    )
    
    st.divider()
    
    # Info section
    st.markdown("### 📊 Data Sources")
    st.markdown("""
    - **OpenWeatherMap**: Current & Forecast
    - **NOAA CDO**: Historical Climate
    """)
    
    st.divider()
    
    st.markdown("### 🔄 Update Frequency")
    st.markdown("""
    - **Weather**: Hourly
    - **Climate**: Daily
    - **Analytics**: Daily
    """)

# Main content tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠 Current Weather",
    "📈 Trends Analysis",
    "🔮 Forecasts",
    "🌍 Weather Patterns",
    "📊 Data Quality"
])

# Tab 1: Current Weather
with tab1:
    st.header("Current Weather Conditions")
    
    current_weather = load_current_weather()
    
    if not current_weather.empty:
        # Display time
        latest_update = current_weather['dt'].max()
        st.info(f"📅 Last Updated: {latest_update.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Metrics in columns
        cols = st.columns(len(current_weather))
        
        for idx, (_, row) in enumerate(current_weather.iterrows()):
            with cols[idx]:
                st.markdown(f"### {row['city_name']}")
                st.metric(
                    label="Temperature",
                    value=f"{row['temperature']:.1f}°C",
                    delta=f"Feels like {row['feels_like']:.1f}°C"
                )
                st.metric(label="Humidity", value=f"{row['humidity']}%")
                st.metric(label="Wind Speed", value=f"{row['wind_speed']:.1f} m/s")
                st.caption(f"☁️ {row['weather_description'].title()}")
        
        st.divider()
        
        # Current weather table
        st.subheader("📋 Detailed View")
        display_df = current_weather[[
            'city_name', 'temperature', 'feels_like', 'humidity', 
            'pressure', 'wind_speed', 'weather_description'
        ]].copy()
        display_df.columns = [
            'City', 'Temp (°C)', 'Feels Like (°C)', 'Humidity (%)',
            'Pressure (hPa)', 'Wind (m/s)', 'Conditions'
        ]
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.warning("⚠️ No current weather data available. Please run the weather ingestion DAG first.")

# Tab 2: Trends Analysis
with tab2:
    st.header("Temperature Trends & Analytics")
    
    daily_weather = load_daily_weather(time_range)
    
    if not daily_weather.empty:
        # City selector
        selected_cities = st.multiselect(
            "Select Cities to Compare",
            options=daily_weather['city_name'].unique(),
            default=daily_weather['city_name'].unique()[:3]
        )
        
        if selected_cities:
            filtered_data = daily_weather[daily_weather['city_name'].isin(selected_cities)]
            
            # Temperature trend chart
            st.subheader("🌡️ Temperature Trends Over Time")
            fig_temp = go.Figure()
            
            for city in selected_cities:
                city_data = filtered_data[filtered_data['city_name'] == city]
                
                # Add average temperature line
                fig_temp.add_trace(go.Scatter(
                    x=city_data['date'],
                    y=city_data['avg_temperature'],
                    name=f"{city} (Avg)",
                    mode='lines+markers',
                    line=dict(width=2)
                ))
                
                # Add min/max range
                fig_temp.add_trace(go.Scatter(
                    x=city_data['date'].tolist() + city_data['date'].tolist()[::-1],
                    y=city_data['max_temperature'].tolist() + city_data['min_temperature'].tolist()[::-1],
                    fill='toself',
                    fillcolor='rgba(0,100,200,0.1)',
                    line=dict(color='rgba(255,255,255,0)'),
                    showlegend=False,
                    name=f"{city} Range"
                ))
            
            fig_temp.update_layout(
                height=500,
                xaxis_title="Date",
                yaxis_title="Temperature (°C)",
                hovermode='x unified',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_temp, use_container_width=True)
            
            # Statistics
            st.subheader("📊 Summary Statistics")
            col1, col2 = st.columns(2)
            
            with col1:
                stats_df = filtered_data.groupby('city_name').agg({
                    'avg_temperature': ['mean', 'min', 'max'],
                    'avg_humidity': 'mean',
                    'avg_wind_speed': 'mean'
                }).round(2)
                stats_df.columns = ['Avg Temp', 'Min Temp', 'Max Temp', 'Avg Humidity', 'Avg Wind']
                st.dataframe(stats_df, use_container_width=True)
            
            with col2:
                # Weather conditions distribution
                condition_dist = filtered_data.groupby(['city_name', 'weather_condition']).size().reset_index(name='count')
                fig_conditions = px.bar(
                    condition_dist,
                    x='city_name',
                    y='count',
                    color='weather_condition',
                    title="Weather Conditions Distribution",
                    labels={'city_name': 'City', 'count': 'Number of Days'}
                )
                st.plotly_chart(fig_conditions, use_container_width=True)
        else:
            st.info("Please select at least one city to view trends.")
    else:
        st.warning("⚠️ No daily weather data available yet. Data will appear after running the pipeline.")

# Tab 3: Forecasts
with tab3:
    st.header("5-Day Weather Forecast")
    
    forecast_data = load_forecast_data()
    
    if not forecast_data.empty:
        # City selector for forecast
        forecast_city = st.selectbox(
            "Select City",
            options=forecast_data['city_name'].unique()
        )
        
        city_forecast = forecast_data[forecast_data['city_name'] == forecast_city].copy()
        city_forecast['date'] = pd.to_datetime(city_forecast['forecast_time']).dt.date
        
        # Forecast chart
        fig_forecast = go.Figure()
        
        fig_forecast.add_trace(go.Scatter(
            x=city_forecast['forecast_time'],
            y=city_forecast['temperature'],
            name='Temperature',
            mode='lines+markers',
            line=dict(color='#FF6B6B', width=3),
            marker=dict(size=8)
        ))
        
        fig_forecast.update_layout(
            title=f"Temperature Forecast for {forecast_city}",
            xaxis_title="Date & Time",
            yaxis_title="Temperature (°C)",
            height=400,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig_forecast, use_container_width=True)
        
        # Forecast details
        st.subheader("📅 Detailed Forecast")
        
        # Group by date
        for date in city_forecast['date'].unique()[:5]:
            with st.expander(f"📆 {date}"):
                date_forecast = city_forecast[city_forecast['date'] == date]
                
                cols = st.columns(len(date_forecast))
                for idx, (_, row) in enumerate(date_forecast.iterrows()):
                    with cols[idx]:
                        time = pd.to_datetime(row['forecast_time']).strftime('%H:%M')
                        st.markdown(f"**{time}**")
                        st.metric("Temp", f"{row['temperature']:.1f}°C")
                        st.caption(f"☁️ {row['weather_description']}")
                        st.caption(f"💧 {row['precipitation_probability']*100:.0f}% rain")
    else:
        st.warning("⚠️ No forecast data available. Please run the weather ingestion DAG.")

# Tab 4: Weather Patterns
with tab4:
    st.header("Weather Patterns & Insights")
    
    patterns = load_weather_patterns()
    trends = load_temperature_trends()
    
    if not patterns.empty:
        # Monthly weather patterns
        st.subheader("🗓️ Monthly Weather Patterns")
        
        selected_pattern_city = st.selectbox(
            "Select City for Pattern Analysis",
            options=patterns['city_name'].unique(),
            key='pattern_city'
        )
        
        city_patterns = patterns[patterns['city_name'] == selected_pattern_city]
        
        # Heatmap of conditions by month
        pivot_patterns = city_patterns.pivot_table(
            index='weather_condition',
            columns='month',
            values='frequency',
            fill_value=0
        )
        
        fig_heatmap = px.imshow(
            pivot_patterns,
            labels=dict(x="Month", y="Weather Condition", color="Frequency"),
            title=f"Weather Condition Frequency by Month - {selected_pattern_city}",
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)
        
    if not trends.empty:
        st.subheader("📈 Temperature Variance Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Temperature variance by city
            latest_trends = trends.sort_values(['year', 'month'], ascending=False).groupby('city_name').first().reset_index()
            
            fig_variance = px.bar(
                latest_trends.sort_values('temperature_variance', ascending=False),
                x='city_name',
                y='temperature_variance',
                title="Temperature Variability by City",
                labels={'city_name': 'City', 'temperature_variance': 'Variance (°C²)'},
                color='temperature_variance',
                color_continuous_scale='Reds'
            )
            st.plotly_chart(fig_variance, use_container_width=True)
        
        with col2:
            # Days above/below average
            fig_days = go.Figure()
            fig_days.add_trace(go.Bar(
                x=latest_trends['city_name'],
                y=latest_trends['days_above_avg'],
                name='Days Above Average',
                marker_color='#FF6B6B'
            ))
            fig_days.add_trace(go.Bar(
                x=latest_trends['city_name'],
                y=latest_trends['days_below_avg'],
                name='Days Below Average',
                marker_color='#4ECDC4'
            ))
            fig_days.update_layout(
                title="Temperature Distribution",
                xaxis_title="City",
                yaxis_title="Number of Days",
                barmode='group'
            )
            st.plotly_chart(fig_days, use_container_width=True)
    
    if patterns.empty and trends.empty:
        st.warning("⚠️ No analytics data available yet. Run the climate analysis DAG to generate insights.")

# Tab 5: Data Quality
with tab5:
    st.header("Data Quality Metrics")
    
    col1, col2, col3 = st.columns(3)
    
    # Count records in each table
    try:
        raw_count = db.execute_query("SELECT COUNT(*) FROM raw.weather_current")[0][0]
        clean_count = db.execute_query("SELECT COUNT(*) FROM clean.weather_daily")[0][0]
        analytics_count = db.execute_query("SELECT COUNT(*) FROM analytics.temperature_trends")[0][0]
        
        with col1:
            st.metric("Raw Weather Records", f"{raw_count:,}")
        with col2:
            st.metric("Clean Daily Records", f"{clean_count:,}")
        with col3:
            st.metric("Analytics Records", f"{analytics_count:,}")
        
        st.divider()
        
        # Data freshness
        st.subheader("📅 Data Freshness")
        
        freshness_query = """
        SELECT 
            'Current Weather' as data_type,
            MAX(dt) as latest_record,
            COUNT(*) as record_count
        FROM raw.weather_current
        UNION ALL
        SELECT 
            'Daily Weather' as data_type,
            MAX(date) as latest_record,
            COUNT(*) as record_count
        FROM clean.weather_daily
        UNION ALL
        SELECT
            'Weather Forecast' as data_type,
            MAX(forecast_time) as latest_record,
            COUNT(*) as record_count
        FROM raw.weather_forecast
        """
        
        freshness_df = db.get_dataframe(freshness_query)
        freshness_df.columns = ['Data Type', 'Latest Record', 'Total Records']
        st.dataframe(freshness_df, use_container_width=True, hide_index=True)
        
        st.divider()
        
        # Pipeline status
        st.subheader("🔄 Pipeline Status")
        
        if raw_count > 0:
            st.success("✅ Weather Ingestion Pipeline: Active")
        else:
            st.error("❌ Weather Ingestion Pipeline: No data")
        
        if clean_count > 0:
            st.success("✅ Data Transformation: Active")
        else:
            st.warning("⚠️ Data Transformation: Pending")
        
        if analytics_count > 0:
            st.success("✅ Analytics Generation: Active")
        else:
            st.warning("⚠️ Analytics Generation: Pending")
            
    except Exception as e:
        st.error(f"Error loading data quality metrics: {e}")
        st.info("Make sure the Airflow DAGs have run at least once to populate the database.")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p>🚀 Built with Apache Airflow, DuckDB, and Streamlit | Data from OpenWeatherMap & NOAA</p>
    <p>📊 <a href='https://github.com/ksarveshvenkatachalam-lang/weather-climate-analytics-pipeline' target='_blank'>View on GitHub</a></p>
</div>
""", unsafe_allow_html=True)
