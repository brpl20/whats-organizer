"""
ZIP file analysis module
"""
import os
import re
from typing import Optional, List, Tuple
from models.zip_analysis import ZipAnalysisData
from models.device import DeviceType
from exceptions.custom_exceptions import ZipAnalysisError, SecurityError

# Security constants
MAX_EXTRACTED_SIZE = 500 * 1024 * 1024  # 500MB
MAX_COMPRESSION_RATIO = 10
MAX_FILES = 10000

# Malicious patterns to check
MALICIOUS_PATTERNS = [
    ".sh", ".bat", ".cmd", ".ps1", ".vbs", ".js", ".exe", ".dll", ".so",
    ".sql", ".db", "DROP TABLE", "DELETE FROM", "INSERT INTO", "SELECT ",
    "shell", "exec(", "system(", "eval(", "<script", "<?php"
]

class ZipAnalyzer:
    """Handles ZIP file analysis and security checks"""
    
    def __init__(self):
        self.analysis_data = ZipAnalysisData()
    
    def analyze_file(self, zip_path: str) -> ZipAnalysisData:
        """
        Analyze a ZIP file for security and extract metadata
        
        Args:
            zip_path: Path to the ZIP file
            
        Returns:
            ZipAnalysisData with analysis results
            
        Raises:
            ZipAnalysisError: If analysis fails
            SecurityError: If security threats are detected
        """
        if not os.path.exists(zip_path):
            raise ZipAnalysisError(f"ZIP file not found: {zip_path}")
        
        # Check file size
        file_size = os.path.getsize(zip_path)
        if file_size > MAX_EXTRACTED_SIZE:
            raise SecurityError(
                f"File too large: {file_size} bytes. "
                f"Maximum allowed: {MAX_EXTRACTED_SIZE} bytes."
            )
        
        try:
            # Import the existing analyze_zip_file function
            from zip_analyser import analyze_zip_file
            analysis_result = analyze_zip_file(zip_path)
            
            self.analysis_data.analysis = analysis_result
            
            # Check for security alerts
            if "SECURITY ALERT" in analysis_result:
                raise SecurityError(
                    "Possible security threat detected in ZIP file. "
                    "Please verify the file."
                )
            
            # Extract device type
            self._detect_device(analysis_result)
            
            # Extract WhatsApp contact for Android
            self._extract_contact(analysis_result)
            
            # Check for malicious files
            self._check_malicious_files(analysis_result)
            
            return self.analysis_data
            
        except ImportError as e:
            raise ZipAnalysisError(f"Failed to import zip_analyser: {e}")
        except Exception as e:
            if isinstance(e, (SecurityError, ZipAnalysisError)):
                raise
            raise ZipAnalysisError(f"ZIP analysis failed: {str(e)}")
    
    def _detect_device(self, analysis_result: str) -> None:
        """Detect device type from ZIP analysis"""
        system_info = ""
        if "Creation systems:" in analysis_result:
            system_info = analysis_result.split("Creation systems:")[1].split("\n")[0].strip()
            self.analysis_data.creation_system = system_info
        
        # Determine device type
        if any(sys in system_info for sys in ["MS-DOS", "OS/2", "Windows", "NTFS", "VFAT", "UNIX"]):
            self.analysis_data.detected_device = DeviceType.ANDROID.value
        elif any(sys in system_info for sys in ["Macintosh", "OS X", "Darwin", "Z-System"]):
            self.analysis_data.detected_device = DeviceType.IPHONE.value
        else:
            self.analysis_data.detected_device = DeviceType.UNKNOWN.value
    
    def _extract_contact(self, analysis_result: str) -> None:
        """Extract WhatsApp contact name from analysis"""
        if self.analysis_data.detected_device == DeviceType.ANDROID.value:
            if "WhatsApp Contacts Found:" in analysis_result:
                contact_section = analysis_result.split("WhatsApp Contacts Found:")[1].split("\n")[1:]
                for line in contact_section:
                    if line.strip().startswith("- "):
                        self.analysis_data.whatsapp_contact = line.strip()[2:].strip()
                        break
    
    def _check_malicious_files(self, analysis_result: str) -> None:
        """Check for potentially malicious files"""
        suspicious_files = []
        suspicious_extensions = [".sh", ".bat", ".cmd", ".ps1", ".vbs", ".js", ".exe", ".dll", ".so"]
        
        # Extract file names from detailed file list
        if "Detailed File List:" in analysis_result:
            file_list_section = analysis_result.split("Detailed File List:")[1]
            lines = file_list_section.split('\n')
            
            for line in lines:
                line = line.strip()
                # Look for filename lines (they don't start with spaces and contain file info)
                if line and not line.startswith(' ') and not line.startswith('\t'):
                    filename = line.split()[0] if line.split() else ""
                    
                    # Check for malicious extensions
                    for ext in suspicious_extensions:
                        if filename.lower().endswith(ext.lower()):
                            suspicious_files.append(filename)
                            print(f"🚨 SECURITY ALERT: Malicious file detected: {filename}")
                            break
        
        # Also check for malicious content patterns in file content analysis
        malicious_content = ["DROP TABLE", "DELETE FROM", "INSERT INTO", "SELECT ", 
                           "shell", "exec(", "system(", "eval(", "<script", "<?php"]
        
        for pattern in malicious_content:
            if pattern.lower() in analysis_result.lower():
                suspicious_files.append(f"content:{pattern}")
        
        if suspicious_files:
            self.analysis_data.suspicious_files = suspicious_files
            raise SecurityError(
                f"🚨 ARQUIVO MALICIOSO DETECTADO! Arquivos perigosos encontrados: {', '.join(suspicious_files)}. "
                f"Por segurança, o processamento foi interrompido."
            )
    
    def extract_iphone_contact(self, chat_file_path: str) -> Optional[str]:
        """
        Extract WhatsApp contact name for iPhone from chat file
        
        Args:
            chat_file_path: Path to _chat.txt file
            
        Returns:
            Contact name or None
        """
        if not os.path.exists(chat_file_path):
            return None
        
        try:
            with open(chat_file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    # iPhone format: [dd/mm/yyyy, hh:mm:ss] Contact Name: message
                    match = re.match(r'\[(\d{2}/\d{2}/\d{4}), (\d{2}:\d{2}:\d{2})\] ([^:]+):', line)
                    if match:
                        contact_name = match.group(3).strip()
                        self.analysis_data.whatsapp_contact = contact_name
                        return contact_name
                        
        except Exception as e:
            print(f"Warning: Could not extract iPhone contact name: {str(e)}")
        
        return None