"""
DuckDB Manager for Weather Analytics
Handles database operations and schema management
"""

import os
import duckdb
import logging
from typing import Optional, List, Dict
from pathlib import Path

logger = logging.getLogger(__name__)


class DuckDBManager:
    """
    Manager for DuckDB operations
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize DuckDB connection
        
        Args:
            db_path: Path to DuckDB database file
        """
        self.db_path = db_path or os.getenv('DUCKDB_PATH', './data/weather_analytics.duckdb')
        
        # Ensure directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.conn = duckdb.connect(self.db_path)
        logger.info(f"Connected to DuckDB at {self.db_path}")
        
        self._create_schemas()
    
    def _create_schemas(self):
        """Create database schemas if they don't exist"""
        schemas = [
            "CREATE SCHEMA IF NOT EXISTS raw",
            "CREATE SCHEMA IF NOT EXISTS clean",
            "CREATE SCHEMA IF NOT EXISTS analytics"
        ]
        
        for schema in schemas:
            self.conn.execute(schema)
        
        logger.info("Database schemas initialized")
    
    def create_raw_weather_table(self):
        """Create raw weather data table"""
        query = """
        CREATE TABLE IF NOT EXISTS raw.weather_current (
            id INTEGER PRIMARY KEY,
            city_name VARCHAR,
            country_code VARCHAR,
            latitude DOUBLE,
            longitude DOUBLE,
            temperature DOUBLE,
            feels_like DOUBLE,
            temp_min DOUBLE,
            temp_max DOUBLE,
            pressure INTEGER,
            humidity INTEGER,
            visibility INTEGER,
            wind_speed DOUBLE,
            wind_deg INTEGER,
            clouds_all INTEGER,
            weather_main VARCHAR,
            weather_description VARCHAR,
            dt TIMESTAMP,
            timezone INTEGER,
            sunrise TIMESTAMP,
            sunset TIMESTAMP,
            extracted_at TIMESTAMP,
            source VARCHAR,
            raw_json JSON
        )
        """
        self.conn.execute(query)
        logger.info("Created raw.weather_current table")
    
    def create_raw_forecast_table(self):
        """Create raw forecast data table"""
        query = """
        CREATE TABLE IF NOT EXISTS raw.weather_forecast (
            forecast_id VARCHAR PRIMARY KEY,
            city_name VARCHAR,
            country_code VARCHAR,
            latitude DOUBLE,
            longitude DOUBLE,
            forecast_time TIMESTAMP,
            temperature DOUBLE,
            feels_like DOUBLE,
            temp_min DOUBLE,
            temp_max DOUBLE,
            pressure INTEGER,
            humidity INTEGER,
            weather_main VARCHAR,
            weather_description VARCHAR,
            clouds_all INTEGER,
            wind_speed DOUBLE,
            wind_deg INTEGER,
            visibility INTEGER,
            pop DOUBLE,
            rain_3h DOUBLE,
            snow_3h DOUBLE,
            extracted_at TIMESTAMP,
            source VARCHAR,
            raw_json JSON
        )
        """
        self.conn.execute(query)
        logger.info("Created raw.weather_forecast table")
    
    def create_raw_climate_table(self):
        """Create raw climate data table from NOAA"""
        query = """
        CREATE TABLE IF NOT EXISTS raw.climate_data (
            record_id VARCHAR PRIMARY KEY,
            station_id VARCHAR,
            location_id VARCHAR,
            date DATE,
            datatype VARCHAR,
            value DOUBLE,
            attributes VARCHAR,
            extracted_at TIMESTAMP,
            source VARCHAR,
            raw_json JSON
        )
        """
        self.conn.execute(query)
        logger.info("Created raw.climate_data table")
    
    def create_clean_weather_table(self):
        """Create cleaned weather data table"""
        query = """
        CREATE TABLE IF NOT EXISTS clean.weather_daily (
            date DATE,
            city_name VARCHAR,
            country_code VARCHAR,
            latitude DOUBLE,
            longitude DOUBLE,
            avg_temperature DOUBLE,
            min_temperature DOUBLE,
            max_temperature DOUBLE,
            avg_humidity INTEGER,
            avg_pressure INTEGER,
            total_precipitation DOUBLE,
            avg_wind_speed DOUBLE,
            weather_condition VARCHAR,
            data_quality_score DOUBLE,
            record_count INTEGER,
            created_at TIMESTAMP,
            PRIMARY KEY (date, city_name, country_code)
        )
        """
        self.conn.execute(query)
        logger.info("Created clean.weather_daily table")
    
    def create_analytics_tables(self):
        """Create analytics tables"""
        
        # Temperature trends
        temp_trends = """
        CREATE TABLE IF NOT EXISTS analytics.temperature_trends (
            city_name VARCHAR,
            country_code VARCHAR,
            year INTEGER,
            month INTEGER,
            avg_temperature DOUBLE,
            min_temperature DOUBLE,
            max_temperature DOUBLE,
            temperature_variance DOUBLE,
            days_above_avg INTEGER,
            days_below_avg INTEGER,
            created_at TIMESTAMP,
            PRIMARY KEY (city_name, country_code, year, month)
        )
        """
        
        # Weather patterns
        weather_patterns = """
        CREATE TABLE IF NOT EXISTS analytics.weather_patterns (
            city_name VARCHAR,
            country_code VARCHAR,
            month INTEGER,
            weather_condition VARCHAR,
            frequency INTEGER,
            avg_temperature DOUBLE,
            avg_precipitation DOUBLE,
            created_at TIMESTAMP
        )
        """
        
        self.conn.execute(temp_trends)
        self.conn.execute(weather_patterns)
        logger.info("Created analytics tables")
    
    def insert_dataframe(self, df, table_name: str, schema: str = 'raw'):
        """Insert pandas DataFrame into table"""
        full_table = f"{schema}.{table_name}"
        self.conn.execute(f"INSERT INTO {full_table} SELECT * FROM df")
        logger.info(f"Inserted {len(df)} rows into {full_table}")
    
    def execute_query(self, query: str) -> List[tuple]:
        """Execute a query and return results"""
        return self.conn.execute(query).fetchall()
    
    def get_dataframe(self, query: str):
        """Execute query and return as pandas DataFrame"""
        return self.conn.execute(query).df()
    
    def close(self):
        """Close database connection"""
        self.conn.close()
        logger.info("DuckDB connection closed")
