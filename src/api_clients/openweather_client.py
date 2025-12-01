"""
OpenWeatherMap API Client
Handles current weather, forecast, and historical data retrieval
"""

import os
import requests
import logging
from datetime import datetime
from typing import Dict, List, Optional
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class OpenWeatherClient:
    """
    Client for interacting with OpenWeatherMap API
    Documentation: https://openweathermap.org/api
    """
    
    BASE_URL = "https://api.openweathermap.org/data/2.5"
    GEO_URL = "http://api.openweathermap.org/geo/1.0"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenWeather API client
        
        Args:
            api_key: OpenWeather API key (defaults to env var)
        """
        self.api_key = api_key or os.getenv('OPENWEATHER_API_KEY')
        if not self.api_key:
            raise ValueError("OpenWeather API key is required")
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'WeatherAnalyticsPipeline/1.0'
        })
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def _make_request(self, endpoint: str, params: Dict) -> Dict:
        """
        Make API request with retry logic
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            
        Returns:
            JSON response as dictionary
        """
        params['appid'] = self.api_key
        
        try:
            response = self.session.get(
                f"{self.BASE_URL}/{endpoint}",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise
    
    def get_current_weather(self, city: str, country_code: Optional[str] = None) -> Dict:
        """
        Get current weather for a city
        
        Args:
            city: City name
            country_code: ISO 3166 country code (e.g., 'GB', 'US')
            
        Returns:
            Current weather data
        """
        location = f"{city},{country_code}" if country_code else city
        
        params = {
            'q': location,
            'units': 'metric'
        }
        
        data = self._make_request('weather', params)
        
        # Add metadata
        data['extracted_at'] = datetime.utcnow().isoformat()
        data['source'] = 'openweathermap'
        
        logger.info(f"Retrieved current weather for {location}")
        return data
    
    def get_forecast(self, city: str, country_code: Optional[str] = None) -> Dict:
        """
        Get 5-day weather forecast with 3-hour intervals
        
        Args:
            city: City name
            country_code: ISO 3166 country code
            
        Returns:
            Forecast data
        """
        location = f"{city},{country_code}" if country_code else city
        
        params = {
            'q': location,
            'units': 'metric'
        }
        
        data = self._make_request('forecast', params)
        
        # Add metadata
        data['extracted_at'] = datetime.utcnow().isoformat()
        data['source'] = 'openweathermap'
        
        logger.info(f"Retrieved forecast for {location}")
        return data
    
    def get_weather_by_coordinates(self, lat: float, lon: float) -> Dict:
        """
        Get current weather by geographic coordinates
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Current weather data
        """
        params = {
            'lat': lat,
            'lon': lon,
            'units': 'metric'
        }
        
        data = self._make_request('weather', params)
        data['extracted_at'] = datetime.utcnow().isoformat()
        data['source'] = 'openweathermap'
        
        logger.info(f"Retrieved weather for coordinates ({lat}, {lon})")
        return data
    
    def get_air_pollution(self, lat: float, lon: float) -> Dict:
        """
        Get air pollution data for coordinates
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Air pollution data
        """
        params = {
            'lat': lat,
            'lon': lon,
            'appid': self.api_key
        }
        
        try:
            response = self.session.get(
                "http://api.openweathermap.org/data/2.5/air_pollution",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            data['extracted_at'] = datetime.utcnow().isoformat()
            data['source'] = 'openweathermap'
            
            logger.info(f"Retrieved air pollution data for ({lat}, {lon})")
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"Air pollution API request failed: {e}")
            raise
    
    def geocode_city(self, city: str, country_code: Optional[str] = None, limit: int = 1) -> List[Dict]:
        """
        Get geographic coordinates for a city
        
        Args:
            city: City name
            country_code: ISO 3166 country code
            limit: Number of results to return
            
        Returns:
            List of location data with coordinates
        """
        location = f"{city},{country_code}" if country_code else city
        
        params = {
            'q': location,
            'limit': limit,
            'appid': self.api_key
        }
        
        try:
            response = self.session.get(
                f"{self.GEO_URL}/direct",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"Geocoded {location}")
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"Geocoding request failed: {e}")
            raise
    
    def close(self):
        """Close the session"""
        self.session.close()
