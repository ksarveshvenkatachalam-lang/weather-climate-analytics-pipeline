"""
Climate Data Analysis DAG
Schedule: Daily
Purpose: Fetch historical climate data from NOAA and generate analytics
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

from src.api_clients.noaa_client import NOAAClient
from src.utils.duckdb_manager import DuckDBManager
from src.utils.data_processor import WeatherDataProcessor
from src.utils.file_manager import FileManager

logger = logging.getLogger(__name__)

# Configuration
LOCATION_ID = 'FIPS:UK'  # United Kingdom

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=10),
    'execution_timeout': timedelta(minutes=60),
}


def fetch_noaa_climate_data(**context):
    """
    Fetch climate data from NOAA for the past 30 days
    """
    logger.info("Fetching NOAA climate data")
    client = NOAAClient()
    file_manager = FileManager()
    
    # Get date range
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    try:
        # Fetch daily summaries
        data = client.get_daily_summaries(
            location_id=LOCATION_ID,
            start_date=start_date,
            end_date=end_date,
            data_types=['TMAX', 'TMIN', 'PRCP', 'SNOW']
        )
        
        # Save raw JSON
        filename = f"noaa_climate_{start_date}_{end_date}.json"
        file_manager.save_raw_json(data, filename, 'raw')
        
        # Push to XCom
        context['task_instance'].xcom_push(key='climate_data', value=data)
        
        logger.info(f"Fetched {len(data['data'])} climate records")
    except Exception as e:
        logger.error(f"Failed to fetch NOAA data: {e}")
        raise
    finally:
        client.close()


def process_and_load_climate_data(**context):
    """
    Process and load NOAA climate data into DuckDB
    """
    task_instance = context['task_instance']
    climate_data = task_instance.xcom_pull(task_ids='fetch_noaa_climate_data', key='climate_data')
    
    if not climate_data or not climate_data['data']:
        logger.warning("No climate data to process")
        return
    
    logger.info(f"Processing {len(climate_data['data'])} climate records")
    processor = WeatherDataProcessor()
    db_manager = DuckDBManager()
    
    try:
        # Process climate data
        df = processor.process_noaa_climate_data(climate_data)
        
        # Load to DuckDB
        db_manager.insert_dataframe(df, 'climate_data', schema='raw')
        
        logger.info(f"Loaded {len(df)} climate records to DuckDB")
    except Exception as e:
        logger.error(f"Error processing climate data: {e}")
        raise
    finally:
        db_manager.close()


def compute_temperature_trends(**context):
    """
    Compute temperature trends analytics
    """
    logger.info("Computing temperature trends")
    db_manager = DuckDBManager()
    
    query = """
    INSERT INTO analytics.temperature_trends
    SELECT 
        city_name,
        country_code,
        YEAR(date) as year,
        MONTH(date) as month,
        AVG(avg_temperature) as avg_temperature,
        MIN(min_temperature) as min_temperature,
        MAX(max_temperature) as max_temperature,
        VARIANCE(avg_temperature) as temperature_variance,
        SUM(CASE WHEN avg_temperature > AVG(avg_temperature) OVER (PARTITION BY city_name) THEN 1 ELSE 0 END) as days_above_avg,
        SUM(CASE WHEN avg_temperature < AVG(avg_temperature) OVER (PARTITION BY city_name) THEN 1 ELSE 0 END) as days_below_avg,
        CURRENT_TIMESTAMP as created_at
    FROM clean.weather_daily
    WHERE date >= CURRENT_DATE - INTERVAL '90 days'
    GROUP BY city_name, country_code, YEAR(date), MONTH(date)
    ON CONFLICT (city_name, country_code, year, month) 
    DO UPDATE SET
        avg_temperature = EXCLUDED.avg_temperature,
        min_temperature = EXCLUDED.min_temperature,
        max_temperature = EXCLUDED.max_temperature,
        temperature_variance = EXCLUDED.temperature_variance,
        days_above_avg = EXCLUDED.days_above_avg,
        days_below_avg = EXCLUDED.days_below_avg,
        created_at = EXCLUDED.created_at
    """
    
    try:
        db_manager.execute_query(query)
        logger.info("Temperature trends computed")
    except Exception as e:
        logger.error(f"Error computing temperature trends: {e}")
        raise
    finally:
        db_manager.close()


def compute_weather_patterns(**context):
    """
    Compute weather pattern analytics
    """
    logger.info("Computing weather patterns")
    db_manager = DuckDBManager()
    
    query = """
    DELETE FROM analytics.weather_patterns;
    
    INSERT INTO analytics.weather_patterns
    SELECT 
        city_name,
        country_code,
        MONTH(date) as month,
        weather_condition,
        COUNT(*) as frequency,
        AVG(avg_temperature) as avg_temperature,
        AVG(total_precipitation) as avg_precipitation,
        CURRENT_TIMESTAMP as created_at
    FROM clean.weather_daily
    WHERE date >= CURRENT_DATE - INTERVAL '365 days'
    GROUP BY city_name, country_code, MONTH(date), weather_condition
    """
    
    try:
        db_manager.execute_query(query)
        logger.info("Weather patterns computed")
    except Exception as e:
        logger.error(f"Error computing weather patterns: {e}")
        raise
    finally:
        db_manager.close()


# Define the DAG
with DAG(
    dag_id='climate_analysis',
    default_args=default_args,
    description='Fetch NOAA climate data and generate analytics',
    schedule_interval='0 2 * * *',  # Run daily at 2 AM
    start_date=days_ago(1),
    catchup=False,
    tags=['climate', 'noaa', 'analytics'],
) as dag:
    
    # Task 1: Fetch NOAA climate data
    fetch_noaa = PythonOperator(
        task_id='fetch_noaa_climate_data',
        python_callable=fetch_noaa_climate_data,
    )
    
    # Task 2: Process and load climate data
    load_climate = PythonOperator(
        task_id='process_load_climate_data',
        python_callable=process_and_load_climate_data,
    )
    
    # Task 3: Compute temperature trends
    temp_trends = PythonOperator(
        task_id='compute_temperature_trends',
        python_callable=compute_temperature_trends,
    )
    
    # Task 4: Compute weather patterns
    weather_patterns = PythonOperator(
        task_id='compute_weather_patterns',
        python_callable=compute_weather_patterns,
    )
    
    # Define task dependencies
    fetch_noaa >> load_climate >> [temp_trends, weather_patterns]
