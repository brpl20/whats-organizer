"""
Device type model
"""
from enum import Enum
from typing import Literal

class DeviceType(Enum):
    """Enum for device types"""
    ANDROID = "android"
    IPHONE = "iphone"
    UNKNOWN = "unknown"
    
    @classmethod
    def from_string(cls, value: str) -> 'DeviceType':
        """Create DeviceType from string"""
        value_lower = value.lower()
        for device in cls:
            if device.value == value_lower:
                return device
        return cls.UNKNOWN
    
    def __str__(self) -> str:
        return self.value

Mobile = Literal["android", "iphone"]