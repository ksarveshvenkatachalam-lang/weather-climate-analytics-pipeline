"""
Weather Data Ingestion DAG
Schedule: Hourly
Purpose: Ingest current weather and forecast data from OpenWeatherMap API
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
import os
import sys
import logging

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from src.api_clients.openweather_client import OpenWeatherClient
from src.utils.duckdb_manager import DuckDBManager
from src.utils.data_processor import WeatherDataProcessor
from src.utils.file_manager import FileManager

logger = logging.getLogger(__name__)

# Configuration
CITIES = os.getenv('TRACKED_CITIES', 'London,Manchester,Liverpool,Edinburgh,Birmingham').split(',')
COUNTRY_CODE = 'GB'

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(minutes=30),
}


def initialize_database(**context):
    """
    Initialize DuckDB database and create tables
    """
    logger.info("Initializing database...")
    db_manager = DuckDBManager()
    
    db_manager.create_raw_weather_table()
    db_manager.create_raw_forecast_table()
    db_manager.create_clean_weather_table()
    db_manager.create_analytics_tables()
    
    db_manager.close()
    logger.info("Database initialization complete")


def fetch_current_weather(**context):
    """
    Fetch current weather for all tracked cities
    """
    logger.info(f"Fetching current weather for {len(CITIES)} cities")
    client = OpenWeatherClient()
    file_manager = FileManager()
    
    weather_data = []
    
    for city in CITIES:
        city = city.strip()
        try:
            data = client.get_current_weather(city, COUNTRY_CODE)
            weather_data.append(data)
            
            # Save raw JSON
            filename = file_manager.generate_filename('current_weather', city)
            file_manager.save_raw_json(data, filename, 'raw')
            
            logger.info(f"Fetched weather for {city}")
        except Exception as e:
            logger.error(f"Failed to fetch weather for {city}: {e}")
    
    client.close()
    
    # Push data to XCom for next task
    context['task_instance'].xcom_push(key='weather_data', value=weather_data)
    logger.info(f"Fetched weather data for {len(weather_data)} cities")


def fetch_weather_forecast(**context):
    """
    Fetch 5-day forecast for all tracked cities
    """
    logger.info(f"Fetching forecasts for {len(CITIES)} cities")
    client = OpenWeatherClient()
    file_manager = FileManager()
    
    forecast_data = []
    
    for city in CITIES:
        city = city.strip()
        try:
            data = client.get_forecast(city, COUNTRY_CODE)
            forecast_data.append(data)
            
            # Save raw JSON
            filename = file_manager.generate_filename('forecast', city)
            file_manager.save_raw_json(data, filename, 'raw')
            
            logger.info(f"Fetched forecast for {city}")
        except Exception as e:
            logger.error(f"Failed to fetch forecast for {city}: {e}")
    
    client.close()
    
    # Push data to XCom
    context['task_instance'].xcom_push(key='forecast_data', value=forecast_data)
    logger.info(f"Fetched forecasts for {len(forecast_data)} cities")


def process_and_load_weather(**context):
    """
    Process and load weather data into DuckDB
    """
    task_instance = context['task_instance']
    weather_data = task_instance.xcom_pull(task_ids='fetch_current_weather', key='weather_data')
    
    if not weather_data:
        logger.warning("No weather data to process")
        return
    
    logger.info(f"Processing {len(weather_data)} weather records")
    processor = WeatherDataProcessor()
    db_manager = DuckDBManager()
    
    # Process each weather record
    for data in weather_data:
        try:
            df = processor.process_current_weather(data)
            db_manager.insert_dataframe(df, 'weather_current', schema='raw')
        except Exception as e:
            logger.error(f"Error processing weather record: {e}")
    
    db_manager.close()
    logger.info("Weather data loaded to DuckDB")


def process_and_load_forecast(**context):
    """
    Process and load forecast data into DuckDB
    """
    task_instance = context['task_instance']
    forecast_data = task_instance.xcom_pull(task_ids='fetch_weather_forecast', key='forecast_data')
    
    if not forecast_data:
        logger.warning("No forecast data to process")
        return
    
    logger.info(f"Processing {len(forecast_data)} forecast datasets")
    processor = WeatherDataProcessor()
    db_manager = DuckDBManager()
    
    # Process each forecast dataset
    for data in forecast_data:
        try:
            df = processor.process_forecast(data)
            db_manager.insert_dataframe(df, 'weather_forecast', schema='raw')
        except Exception as e:
            logger.error(f"Error processing forecast data: {e}")
    
    db_manager.close()
    logger.info("Forecast data loaded to DuckDB")


def aggregate_daily_weather(**context):
    """
    Aggregate weather data to daily summaries
    """
    logger.info("Aggregating weather data to daily summaries")
    db_manager = DuckDBManager()
    processor = WeatherDataProcessor()
    
    # Get today's weather data
    query = """
    SELECT * FROM raw.weather_current
    WHERE DATE(dt) = CURRENT_DATE
    """
    
    df = db_manager.get_dataframe(query)
    
    if df.empty:
        logger.warning("No weather data for today")
        db_manager.close()
        return
    
    # Aggregate to daily
    daily_df = processor.aggregate_daily_weather(df)
    
    # Insert into clean table
    db_manager.insert_dataframe(daily_df, 'weather_daily', schema='clean')
    
    db_manager.close()
    logger.info(f"Aggregated {len(daily_df)} daily weather records")


# Define the DAG
with DAG(
    dag_id='weather_ingestion',
    default_args=default_args,
    description='Ingest current weather and forecast data from OpenWeatherMap',
    schedule_interval='0 * * * *',  # Run hourly
    start_date=days_ago(1),
    catchup=False,
    tags=['weather', 'ingestion', 'openweather'],
) as dag:
    
    # Task 1: Initialize database
    init_db = PythonOperator(
        task_id='initialize_database',
        python_callable=initialize_database,
    )
    
    # Task 2: Fetch current weather
    fetch_weather = PythonOperator(
        task_id='fetch_current_weather',
        python_callable=fetch_current_weather,
    )
    
    # Task 3: Fetch forecast
    fetch_forecast = PythonOperator(
        task_id='fetch_weather_forecast',
        python_callable=fetch_weather_forecast,
    )
    
    # Task 4: Process and load weather data
    load_weather = PythonOperator(
        task_id='process_load_weather',
        python_callable=process_and_load_weather,
    )
    
    # Task 5: Process and load forecast data
    load_forecast = PythonOperator(
        task_id='process_load_forecast',
        python_callable=process_and_load_forecast,
    )
    
    # Task 6: Aggregate to daily summaries
    aggregate_daily = PythonOperator(
        task_id='aggregate_daily_weather',
        python_callable=aggregate_daily_weather,
    )
    
    # Define task dependencies
    init_db >> [fetch_weather, fetch_forecast]
    fetch_weather >> load_weather >> aggregate_daily
    fetch_forecast >> load_forecast
