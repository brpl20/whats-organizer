"""
Media processing module for audio and PDF files
"""
import os
from typing import Dict, List, Any
from exceptions.custom_exceptions import MediaProcessingError

class MediaProcessor:
    """Handles media file processing (audio, PDF, images)"""
    
    def __init__(self, working_folder: str):
        self.working_folder = working_folder
        self.transcriptions: Dict[str, str] = {}
        self.pdf_images: Dict[str, List[str]] = {}
    
    def process_audio_files(self) -> Dict[str, str]:
        """
        Convert audio files and generate transcriptions
        
        Returns:
            Dictionary of filename to transcription text
            
        Raises:
            MediaProcessingError: If audio processing fails
        """
        try:
            from utils.converter_mp3 import convert_opus_to_mp3
            self.transcriptions = convert_opus_to_mp3(self.working_folder)
            return self.transcriptions
        except ImportError as e:
            raise MediaProcessingError(f"Failed to import audio converter: {e}")
        except Exception as e:
            raise MediaProcessingError(f"Audio processing failed: {str(e)}")
    
    def process_pdf_files(self) -> Dict[str, List[str]]:
        """
        Process PDF files and convert to images
        
        Returns:
            Dictionary of PDF filename to list of image paths
            
        Raises:
            MediaProcessingError: If PDF processing fails
        """
        try:
            from utils.converter_pdf import process_pdf_folder
            self.pdf_images = process_pdf_folder(self.working_folder)
            return self.pdf_images
        except ImportError as e:
            raise MediaProcessingError(f"Failed to import PDF converter: {e}")
        except Exception as e:
            raise MediaProcessingError(f"PDF processing failed: {str(e)}")
    
    def append_transcriptions(self, messages: List[Any]) -> List[Any]:
        """
        Append transcriptions to messages
        
        Args:
            messages: List of message objects
            
        Returns:
            Messages with transcriptions appended
        """
        try:
            from utils.file_append import file_appending
            return file_appending(messages, self.transcriptions)
        except ImportError as e:
            raise MediaProcessingError(f"Failed to import file appending: {e}")
        except Exception as e:
            raise MediaProcessingError(f"Failed to append transcriptions: {str(e)}")
    
    def append_pdf_images(self, messages: List[Any]) -> List[Any]:
        """
        Append PDF images to messages
        
        Args:
            messages: List of message objects
            
        Returns:
            Messages with PDF images appended
        """
        try:
            from utils.file_append import file_appending_pdf
            return file_appending_pdf(messages, self.pdf_images)
        except ImportError as e:
            raise MediaProcessingError(f"Failed to import PDF appending: {e}")
        except Exception as e:
            raise MediaProcessingError(f"Failed to append PDF images: {str(e)}")
    
    def process_all_media(self) -> tuple[Dict[str, str], Dict[str, List[str]]]:
        """
        Process all media files (audio and PDF)
        
        Returns:
            Tuple of (transcriptions, pdf_images)
            
        Raises:
            MediaProcessingError: If media processing fails
        """
        print('Converting audio and transcribing...')
        transcriptions = self.process_audio_files()
        
        print('Processing PDFs and Office documents...')
        pdf_images = self.process_pdf_files()
        
        return transcriptions, pdf_images