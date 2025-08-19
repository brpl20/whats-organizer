"""
Exception module for WhatsApp Processor
"""
from .custom_exceptions import (
    WhatsAppProcessorError,
    ZipAnalysisError,
    SecurityError,
    FileProcessingError,
    DeviceDetectionError,
    MediaProcessingError,
    MessageExtractionError
)

__all__ = [
    'WhatsAppProcessorError',
    'ZipAnalysisError',
    'SecurityError',
    'FileProcessingError',
    'DeviceDetectionError',
    'MediaProcessingError',
    'MessageExtractionError'
]