"""
Data models for WhatsApp Processor
"""
from .message import MessageData, MessagesStore
from .device import DeviceType
from core.zip_analysis import ZipAnalysisData

__all__ = [
    'MessageData',
    'MessagesStore',
    'DeviceType',
    'ZipAnalysisData'
]