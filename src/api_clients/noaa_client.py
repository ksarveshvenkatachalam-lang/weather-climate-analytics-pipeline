"""
NOAA Climate Data Online (CDO) API Client
Handles historical climate data retrieval
"""

import os
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class NOAAClient:
    """
    Client for interacting with NOAA Climate Data Online API
    Documentation: https://www.ncdc.noaa.gov/cdo-web/webservices/v2
    """
    
    BASE_URL = "https://www.ncei.noaa.gov/cdo-web/api/v2"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize NOAA CDO API client
        
        Args:
            api_key: NOAA API token (defaults to env var)
        """
        self.api_key = api_key or os.getenv('NOAA_API_KEY')
        if not self.api_key:
            raise ValueError("NOAA API key is required")
        
        self.session = requests.Session()
        self.session.headers.update({
            'token': self.api_key,
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
        try:
            response = self.session.get(
                f"{self.BASE_URL}/{endpoint}",
                params=params,
                timeout=15
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"NOAA API request failed: {e}")
            raise
    
    def get_datasets(self) -> List[Dict]:
        """
        Get available NOAA datasets
        
        Returns:
            List of dataset information
        """
        data = self._make_request('datasets', {'limit': 1000})
        logger.info(f"Retrieved {len(data.get('results', []))} datasets")
        return data.get('results', [])
    
    def get_data_categories(self, dataset_id: str = 'GHCND') -> List[Dict]:
        """
        Get data categories for a dataset
        
        Args:
            dataset_id: Dataset identifier (default: GHCND - Daily Summaries)
            
        Returns:
            List of data categories
        """
        params = {
            'datasetid': dataset_id,
            'limit': 1000
        }
        data = self._make_request('datacategories', params)
        return data.get('results', [])
    
    def get_stations(self, dataset_id: str = 'GHCND', 
                    location_id: Optional[str] = None,
                    limit: int = 100) -> List[Dict]:
        """
        Get weather stations
        
        Args:
            dataset_id: Dataset identifier
            location_id: Location ID (e.g., 'FIPS:UK' for United Kingdom)
            limit: Maximum number of results
            
        Returns:
            List of station information
        """
        params = {
            'datasetid': dataset_id,
            'limit': limit
        }
        
        if location_id:
            params['locationid'] = location_id
        
        data = self._make_request('stations', params)
        logger.info(f"Retrieved {len(data.get('results', []))} stations")
        return data.get('results', [])
    
    def get_climate_data(self, 
                        dataset_id: str = 'GHCND',
                        station_id: Optional[str] = None,
                        location_id: Optional[str] = None,
                        start_date: Optional[str] = None,
                        end_date: Optional[str] = None,
                        datatypeid: Optional[str] = None,
                        limit: int = 1000) -> Dict:
        """
        Get climate data records
        
        Args:
            dataset_id: Dataset identifier (GHCND, GSOM, etc.)
            station_id: Specific station ID
            location_id: Location ID (e.g., 'FIPS:UK')
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            datatypeid: Data type (TMAX, TMIN, PRCP, etc.)
            limit: Maximum number of results
            
        Returns:
            Climate data records
        """
        # Default to last 30 days if no dates provided
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        params = {
            'datasetid': dataset_id,
            'startdate': start_date,
            'enddate': end_date,
            'limit': limit,
            'units': 'metric'
        }
        
        if station_id:
            params['stationid'] = station_id
        if location_id:
            params['locationid'] = location_id
        if datatypeid:
            params['datatypeid'] = datatypeid
        
        data = self._make_request('data', params)
        
        # Add metadata
        result = {
            'data': data.get('results', []),
            'metadata': data.get('metadata', {}),
            'extracted_at': datetime.utcnow().isoformat(),
            'source': 'noaa_cdo',
            'query_params': params
        }
        
        logger.info(f"Retrieved {len(result['data'])} climate records")
        return result
    
    def get_daily_summaries(self,
                          location_id: str,
                          start_date: str,
                          end_date: str,
                          data_types: Optional[List[str]] = None) -> Dict:
        """
        Get daily climate summaries (GHCND dataset)
        
        Args:
            location_id: Location ID (e.g., 'FIPS:UK')
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            data_types: List of data types (TMAX, TMIN, PRCP, SNOW, etc.)
            
        Returns:
            Daily summary data
        """
        if not data_types:
            data_types = ['TMAX', 'TMIN', 'PRCP', 'SNOW']
        
        all_data = []
        
        for data_type in data_types:
            try:
                result = self.get_climate_data(
                    dataset_id='GHCND',
                    location_id=location_id,
                    start_date=start_date,
                    end_date=end_date,
                    datatypeid=data_type,
                    limit=1000
                )
                all_data.extend(result['data'])
            except Exception as e:
                logger.warning(f"Failed to retrieve {data_type}: {e}")
        
        return {
            'data': all_data,
            'location_id': location_id,
            'start_date': start_date,
            'end_date': end_date,
            'extracted_at': datetime.utcnow().isoformat(),
            'source': 'noaa_cdo'
        }
    
    def get_locations(self, dataset_id: str = 'GHCND', limit: int = 1000) -> List[Dict]:
        """
        Get available locations
        
        Args:
            dataset_id: Dataset identifier
            limit: Maximum number of results
            
        Returns:
            List of locations
        """
        params = {
            'datasetid': dataset_id,
            'limit': limit
        }
        
        data = self._make_request('locations', params)
        logger.info(f"Retrieved {len(data.get('results', []))} locations")
        return data.get('results', [])
    
    def close(self):
        """Close the session"""
        self.session.close()
