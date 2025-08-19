"""
Custom exceptions for WhatsApp Processor
"""

class WhatsAppProcessorError(Exception):
    """Base exception for WhatsApp Processor"""
    pass

class ZipAnalysisError(WhatsAppProcessorError):
    """Raised when ZIP analysis fails"""
    pass

class SecurityError(WhatsAppProcessorError):
    """Raised when security threats are detected"""
    pass

class FileProcessingError(WhatsAppProcessorError):
    """Raised when file processing fails"""
    pass

class DeviceDetectionError(WhatsAppProcessorError):
    """Raised when device type cannot be determined"""
    pass

class MediaProcessingError(WhatsAppProcessorError):
    """Raised when media processing fails"""
    pass

class MessageExtractionError(WhatsAppProcessorError):
    """Raised when message extraction fails"""
    pass