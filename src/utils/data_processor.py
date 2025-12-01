"""
Weather Data Processor
Handles transformation and cleaning of weather data
"""

import pandas as pd
import logging
from datetime import datetime
from typing import Dict, List

logger = logging.getLogger(__name__)


class WeatherDataProcessor:
    """
    Processor for transforming raw weather data
    """
    
    @staticmethod
    def process_current_weather(raw_data: Dict) -> pd.DataFrame:
        """
        Process current weather API response into structured format
        
        Args:
            raw_data: Raw JSON response from OpenWeather API
            
        Returns:
            Processed DataFrame
        """
        try:
            processed = {
                'id': raw_data['id'],
                'city_name': raw_data['name'],
                'country_code': raw_data['sys']['country'],
                'latitude': raw_data['coord']['lat'],
                'longitude': raw_data['coord']['lon'],
                'temperature': raw_data['main']['temp'],
                'feels_like': raw_data['main']['feels_like'],
                'temp_min': raw_data['main']['temp_min'],
                'temp_max': raw_data['main']['temp_max'],
                'pressure': raw_data['main']['pressure'],
                'humidity': raw_data['main']['humidity'],
                'visibility': raw_data.get('visibility', None),
                'wind_speed': raw_data['wind']['speed'],
                'wind_deg': raw_data['wind'].get('deg', None),
                'clouds_all': raw_data['clouds']['all'],
                'weather_main': raw_data['weather'][0]['main'],
                'weather_description': raw_data['weather'][0]['description'],
                'dt': pd.to_datetime(raw_data['dt'], unit='s'),
                'timezone': raw_data['timezone'],
                'sunrise': pd.to_datetime(raw_data['sys']['sunrise'], unit='s'),
                'sunset': pd.to_datetime(raw_data['sys']['sunset'], unit='s'),
                'extracted_at': pd.to_datetime(raw_data['extracted_at']),
                'source': raw_data['source'],
                'raw_json': str(raw_data)
            }
            
            df = pd.DataFrame([processed])
            logger.info(f"Processed current weather for {processed['city_name']}")
            return df
            
        except Exception as e:
            logger.error(f"Error processing current weather data: {e}")
            raise
    
    @staticmethod
    def process_forecast(raw_data: Dict) -> pd.DataFrame:
        """
        Process forecast API response into structured format
        
        Args:
            raw_data: Raw JSON response from OpenWeather API
            
        Returns:
            Processed DataFrame
        """
        try:
            city_info = raw_data['city']
            forecast_list = []
            
            for item in raw_data['list']:
                processed = {
                    'forecast_id': f"{city_info['id']}_{item['dt']}",
                    'city_name': city_info['name'],
                    'country_code': city_info['country'],
                    'latitude': city_info['coord']['lat'],
                    'longitude': city_info['coord']['lon'],
                    'forecast_time': pd.to_datetime(item['dt'], unit='s'),
                    'temperature': item['main']['temp'],
                    'feels_like': item['main']['feels_like'],
                    'temp_min': item['main']['temp_min'],
                    'temp_max': item['main']['temp_max'],
                    'pressure': item['main']['pressure'],
                    'humidity': item['main']['humidity'],
                    'weather_main': item['weather'][0]['main'],
                    'weather_description': item['weather'][0]['description'],
                    'clouds_all': item['clouds']['all'],
                    'wind_speed': item['wind']['speed'],
                    'wind_deg': item['wind'].get('deg', None),
                    'visibility': item.get('visibility', None),
                    'pop': item.get('pop', 0),
                    'rain_3h': item.get('rain', {}).get('3h', 0),
                    'snow_3h': item.get('snow', {}).get('3h', 0),
                    'extracted_at': pd.to_datetime(raw_data['extracted_at']),
                    'source': raw_data['source'],
                    'raw_json': str(item)
                }
                forecast_list.append(processed)
            
            df = pd.DataFrame(forecast_list)
            logger.info(f"Processed {len(df)} forecast records for {city_info['name']}")
            return df
            
        except Exception as e:
            logger.error(f"Error processing forecast data: {e}")
            raise
    
    @staticmethod
    def process_noaa_climate_data(raw_data: Dict) -> pd.DataFrame:
        """
        Process NOAA climate data response
        
        Args:
            raw_data: Raw response from NOAA API
            
        Returns:
            Processed DataFrame
        """
        try:
            records = []
            
            for item in raw_data['data']:
                processed = {
                    'record_id': f"{item['station']}_{item['date']}_{item['datatype']}",
                    'station_id': item['station'],
                    'location_id': raw_data.get('query_params', {}).get('locationid', None),
                    'date': pd.to_datetime(item['date']),
                    'datatype': item['datatype'],
                    'value': item['value'],
                    'attributes': item.get('attributes', ''),
                    'extracted_at': pd.to_datetime(raw_data['extracted_at']),
                    'source': raw_data['source'],
                    'raw_json': str(item)
                }
                records.append(processed)
            
            df = pd.DataFrame(records)
            logger.info(f"Processed {len(df)} NOAA climate records")
            return df
            
        except Exception as e:
            logger.error(f"Error processing NOAA climate data: {e}")
            raise
    
    @staticmethod
    def aggregate_daily_weather(df: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregate weather data to daily summaries
        
        Args:
            df: DataFrame with weather records
            
        Returns:
            Daily aggregated DataFrame
        """
        df['date'] = pd.to_datetime(df['dt']).dt.date
        
        daily = df.groupby(['date', 'city_name', 'country_code']).agg({
            'latitude': 'first',
            'longitude': 'first',
            'temperature': 'mean',
            'temp_min': 'min',
            'temp_max': 'max',
            'humidity': 'mean',
            'pressure': 'mean',
            'wind_speed': 'mean',
            'weather_main': lambda x: x.mode()[0] if len(x.mode()) > 0 else x.iloc[0],
            'id': 'count'
        }).reset_index()
        
        daily.columns = [
            'date', 'city_name', 'country_code', 'latitude', 'longitude',
            'avg_temperature', 'min_temperature', 'max_temperature',
            'avg_humidity', 'avg_pressure', 'avg_wind_speed',
            'weather_condition', 'record_count'
        ]
        
        daily['total_precipitation'] = 0.0  # Placeholder
        daily['data_quality_score'] = 1.0
        daily['created_at'] = datetime.utcnow()
        
        logger.info(f"Aggregated to {len(daily)} daily records")
        return daily
