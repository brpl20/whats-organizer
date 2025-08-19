"""
Message extraction module
"""
import os
from typing import List, Dict, Any, Tuple, Optional, Callable
from models.message import MessageData
from models.device import DeviceType
from exceptions.custom_exceptions import MessageExtractionError

class MessageExtractor:
    """Handles message extraction from WhatsApp files"""
    
    def __init__(self, working_folder: str):
        self.working_folder = working_folder
    
    def find_main_chat_file(self, file_list: List[Dict[str, Any]]) -> str:
        """
        Find the main WhatsApp chat file
        
        Args:
            file_list: List of file objects with name and path
            
        Returns:
            Filename of the main chat file
            
        Raises:
            MessageExtractionError: If chat file is not found
        """
        try:
            from find_whats_key_data import find_whats_key
            return find_whats_key(file_list)
        except ImportError as e:
            raise MessageExtractionError(f"Failed to import find_whats_key_data: {e}")
        except Exception as e:
            raise MessageExtractionError(f"Failed to find main chat file: {str(e)}")
    
    def fix_chat_file(self, chat_file_path: str, device_type: str) -> str:
        """
        Fix and prepare the chat file for processing
        
        Args:
            chat_file_path: Path to the main chat file
            device_type: Type of device (android/iphone)
            
        Returns:
            Path to the fixed file
            
        Raises:
            MessageExtractionError: If file fixing fails
        """
        try:
            from file_fixer import process_file_fixer
            return process_file_fixer(chat_file_path, device_type)
        except ImportError as e:
            raise MessageExtractionError(f"Failed to import file_fixer: {e}")
        except Exception as e:
            raise MessageExtractionError(f"Failed to fix chat file: {str(e)}")
    
    def extract_android_messages(
        self, 
        fixed_file: str, 
        whatsapp_contact: Optional[str],
        attached_files: Tuple[Optional[str], ...]
    ) -> List[MessageData]:
        """
        Extract messages from Android WhatsApp export
        
        Args:
            fixed_file: Path to the fixed chat file
            whatsapp_contact: WhatsApp contact name
            attached_files: Tuple of attached file names
            
        Returns:
            List of extracted messages
            
        Raises:
            MessageExtractionError: If extraction fails
        """
        try:
            from extract_objects import extract_info_android
            return extract_info_android(whatsapp_contact, fixed_file, attached_files)
        except ImportError as e:
            raise MessageExtractionError(f"Failed to import extract_objects: {e}")
        except Exception as e:
            raise MessageExtractionError(f"Android message extraction failed: {str(e)}")
    
    def extract_iphone_messages(
        self,
        fixed_file: str,
        attached_files: Tuple[Optional[str], ...]
    ) -> List[MessageData]:
        """
        Extract messages from iPhone WhatsApp export
        
        Args:
            fixed_file: Path to the fixed chat file
            attached_files: Tuple of attached file names
            
        Returns:
            List of extracted messages
            
        Raises:
            MessageExtractionError: If extraction fails
        """
        try:
            from extract_objects import extract_info_iphone
            return extract_info_iphone(fixed_file, attached_files)
        except ImportError as e:
            raise MessageExtractionError(f"Failed to import extract_objects: {e}")
        except Exception as e:
            raise MessageExtractionError(f"iPhone message extraction failed: {str(e)}")
    
    def extract_messages(
        self,
        file_list: List[Dict[str, Any]],
        device_type: str,
        whatsapp_contact: Optional[str] = None
    ) -> List[MessageData]:
        """
        Extract messages based on device type
        
        Args:
            file_list: List of files in the working folder
            device_type: Type of device (android/iphone)
            whatsapp_contact: WhatsApp contact name (for Android)
            
        Returns:
            List of extracted messages
            
        Raises:
            MessageExtractionError: If extraction fails
        """
        # Find main chat file
        main_chat_file = self.find_main_chat_file(file_list)
        main_chat_path = os.path.join(self.working_folder, main_chat_file)
        
        # Fix the chat file
        fixed_file = self.fix_chat_file(main_chat_path, device_type)
        
        # Prepare attached files tuple
        attached_files = tuple(obj['name'] for obj in file_list if obj.get('name'))
        
        # Extract messages based on device type
        if device_type == DeviceType.ANDROID.value:
            print('Android detected!')
            return self.extract_android_messages(fixed_file, whatsapp_contact, attached_files)
        elif device_type == DeviceType.IPHONE.value:
            print('iPhone detected!')
            return self.extract_iphone_messages(fixed_file, attached_files)
        else:
            raise MessageExtractionError(f"Unknown device type: {device_type}")
    
    def get_extraction_function(self, device_type: str) -> Callable:
        """
        Get the appropriate extraction function for the device type
        
        Args:
            device_type: Type of device (android/iphone)
            
        Returns:
            Extraction function for the device
            
        Raises:
            MessageExtractionError: If device type is unsupported
        """
        try:
            from extract_objects import extract_info_android, extract_info_iphone
            
            extract_functions = {
                DeviceType.ANDROID.value: lambda fixed_file, attached_files, contact=None: 
                    extract_info_android(contact, fixed_file, attached_files),
                DeviceType.IPHONE.value: lambda fixed_file, attached_files, contact=None:
                    extract_info_iphone(fixed_file, attached_files),
            }
            
            if device_type not in extract_functions:
                raise MessageExtractionError(f"Unsupported device type: {device_type}")
            
            return extract_functions[device_type]
            
        except ImportError as e:
            raise MessageExtractionError(f"Failed to import extraction functions: {e}")