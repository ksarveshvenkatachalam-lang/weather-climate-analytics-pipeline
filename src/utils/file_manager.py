"""
File Manager for Data Storage
Handles reading and writing data files
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class FileManager:
    """
    Manager for file operations
    """
    
    def __init__(self, base_path: str = './data'):
        """
        Initialize file manager
        
        Args:
            base_path: Base directory for data files
        """
        self.base_path = Path(base_path)
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create directory structure if it doesn't exist"""
        directories = ['raw', 'clean', 'analytics']
        for dir_name in directories:
            (self.base_path / dir_name).mkdir(parents=True, exist_ok=True)
        logger.info("Data directories verified")
    
    def save_raw_json(self, data: Dict, filename: str, subdirectory: str = 'raw') -> str:
        """
        Save raw JSON data to file
        
        Args:
            data: Data to save
            filename: Name of the file
            subdirectory: Subdirectory within base path
            
        Returns:
            Path to saved file
        """
        filepath = self.base_path / subdirectory / filename
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        logger.info(f"Saved data to {filepath}")
        return str(filepath)
    
    def load_json(self, filename: str, subdirectory: str = 'raw') -> Optional[Dict]:
        """
        Load JSON data from file
        
        Args:
            filename: Name of the file
            subdirectory: Subdirectory within base path
            
        Returns:
            Loaded data or None if file doesn't exist
        """
        filepath = self.base_path / subdirectory / filename
        
        if not filepath.exists():
            logger.warning(f"File not found: {filepath}")
            return None
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        logger.info(f"Loaded data from {filepath}")
        return data
    
    def generate_filename(self, prefix: str, city: str, extension: str = 'json') -> str:
        """
        Generate timestamped filename
        
        Args:
            prefix: Filename prefix
            city: City name
            extension: File extension
            
        Returns:
            Generated filename
        """
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"{prefix}_{city}_{timestamp}.{extension}"
        return filename
