"""
File handling utilities for the research logger.
Provides consistent file operations with error handling and type safety.
"""

from pathlib import Path
import json
from typing import Any, Dict, Optional
from datetime import datetime
import shutil

class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles datetime objects."""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

def save_json(data: Any, filepath: Path, create_dirs: bool = True) -> None:
    """
    Safely saves data to a JSON file with proper error handling.
    
    Args:
        data: The data to save
        filepath: Path to the target file
        create_dirs: Whether to create parent directories if they don't exist
    """
    try:
        if create_dirs:
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, cls=DateTimeEncoder)
    except Exception as e:
        raise IOError(f"Failed to save JSON file {filepath}: {str(e)}")

def load_json(filepath: Path) -> Optional[Any]:
    """
    Safely loads data from a JSON file with proper error handling.
    
    Args:
        filepath: Path to the JSON file
        
    Returns:
        The loaded data or None if the file doesn't exist
    """
    if not filepath.exists():
        return None
        
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        raise IOError(f"Failed to load JSON file {filepath}: {str(e)}")

def create_backup(source_dir: Path, backup_dir: Path) -> Path:
    """
    Creates a backup of a directory with timestamp.
    
    Args:
        source_dir: Directory to backup
        backup_dir: Directory to store backups
        
    Returns:
        Path to the created backup
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"backup_{timestamp}"
    
    try:
        shutil.copytree(source_dir, backup_path)
        return backup_path
    except Exception as e:
        raise IOError(f"Failed to create backup: {str(e)}")