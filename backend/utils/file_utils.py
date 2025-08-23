"""
File utility functions
"""
import os
import json
from typing import Dict, Any, List, Optional
from pathlib import Path

class FileUtils:
    """Utility class for file operations"""
    
    @staticmethod
    def ensure_directory_exists(directory: str) -> None:
        """Create directory if it doesn't exist"""
        os.makedirs(directory, exist_ok=True)
    
    @staticmethod
    def save_json(data: Any, file_path: str, indent: int = 2) -> None:
        """Save data to JSON file"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=indent)
    
    @staticmethod
    def load_json(file_path: str) -> Any:
        """Load data from JSON file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def get_file_size_mb(file_path: str) -> float:
        """Get file size in MB"""
        if os.path.exists(file_path):
            return os.path.getsize(file_path) / (1024 * 1024)
        return 0.0
    
    @staticmethod
    def get_file_extension(file_path: str) -> str:
        """Get file extension"""
        return Path(file_path).suffix.lower()
    
    @staticmethod
    def get_filename_without_extension(file_path: str) -> str:
        """Get filename without extension"""
        return Path(file_path).stem
    
    @staticmethod
    def is_media_file(file_path: str) -> bool:
        """Check if file is a media file"""
        media_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.mp4', '.mp3', '.wav', '.opus', '.pdf'}
        return FileUtils.get_file_extension(file_path) in media_extensions
    
    @staticmethod
    def clean_filename(filename: str) -> str:
        """Clean filename by removing invalid characters"""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename
    
    @staticmethod
    def get_safe_path(base_path: str, filename: str) -> str:
        """Get safe file path by combining base path with cleaned filename"""
        clean_name = FileUtils.clean_filename(filename)
        return os.path.join(base_path, clean_name)