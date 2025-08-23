"""
ZIP analysis data model
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

@dataclass
class ZipAnalysisData:
    """Data structure for ZIP analysis results"""
    analysis: str = ""
    detected_device: Optional[str] = None
    whatsapp_contact: Optional[str] = None
    file_count: int = 0
    extracted_size: int = 0
    compression_ratio: float = 0.0
    suspicious_files: List[str] = field(default_factory=list)
    creation_system: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "analysis": self.analysis,
            "detected_device": self.detected_device,
            "whatsapp_contact": self.whatsapp_contact,
            "file_count": self.file_count,
            "extracted_size": self.extracted_size,
            "compression_ratio": self.compression_ratio,
            "suspicious_files": self.suspicious_files,
            "creation_system": self.creation_system
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ZipAnalysisData':
        """Create from dictionary"""
        return cls(**data)