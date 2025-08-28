"""
Main conversation processing orchestrator
"""
import os
import json
import shutil
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from models.message import MessageData
from models.zip_analysis import ZipAnalysisData
from models.device import DeviceType
from exceptions.custom_exceptions import (
    FileProcessingError,
    DeviceDetectionError,
    SecurityError
)
from .zip_analyzer import ZipAnalyzer
from .media_processor import MediaProcessor  
from .message_extractor import MessageExtractor

class ConversationProcessor:
    """Main orchestrator for processing WhatsApp conversations"""
    
    def __init__(self, base_folder: str = "./zip_tests/"):
        self.base_folder = base_folder
        self.zip_analyzer = None
        self.media_processor = None
        self.message_extractor = None
        self.working_folder = ""
        self.analysis_data = ZipAnalysisData()
    
    def process_conversation(self, file_path: str, unique_folder_name: str) -> Dict[str, Any]:
        """
        Process a WhatsApp ZIP file completely
        
        Args:
            file_path: Path to the ZIP file
            unique_folder_name: Unique folder name for processing
            
        Returns:
            Processing results or error dictionary
        """
        try:
            # Setup working environment
            self._setup_working_environment(file_path, unique_folder_name)
            
            # Analyze ZIP file
            self._analyze_zip_file()
            
            # Extract ZIP contents
            self._extract_zip_contents()
            
            # List files in directory
            file_list = self._list_files()
            
            # Handle iPhone contact extraction if needed
            self._handle_iphone_contact_extraction()
            
            # Process media files
            transcriptions, pdf_images = self._process_media()
            
            # Extract messages
            messages = self._extract_messages(file_list)
            
            # Append media to messages
            messages = self._append_media_to_messages(messages, transcriptions, pdf_images)
            
            # Save results
            result = self._save_results(messages)
            
            print('Processing completed!')
            return {
                "sucesso": True,
                "resultado": result,
                "analise": self.analysis_data.to_dict()
            }
            
        except SecurityError as e:
            # Security errors should be returned as-is to trigger special frontend handling
            return {"Erro": str(e)}
        except Exception as e:
            return {"Erro": str(e)}
    
    def _setup_working_environment(self, file_path: str, unique_folder_name: str) -> None:
        """Setup the working directory and copy the ZIP file"""
        if not os.path.exists(file_path):
            raise FileProcessingError(f"File not found: {file_path}")
        
        # Create working directory
        self.working_folder = os.path.join(self.base_folder, unique_folder_name)
        os.makedirs(self.working_folder, exist_ok=True)
        
        # Copy ZIP file to working directory
        print('Copying ZIP file...')
        zip_path = os.path.join(self.working_folder, "uploaded.zip")
        try:
            shutil.copy2(file_path, zip_path)
            self.zip_path = zip_path
        except Exception as e:
            raise FileProcessingError(f"Error copying file: {str(e)}")
    
    def _analyze_zip_file(self) -> None:
        """Analyze the ZIP file for security and metadata"""
        print('Analyzing ZIP file for security...')
        self.zip_analyzer = ZipAnalyzer()

        self.analysis_data = self.zip_analyzer.analyze_file(self.zip_path)
        self.analysis_data.detected_device = self.analysis_data.detected_device or DeviceType.ANDROID.value
    
    def _extract_zip_contents(self) -> None:
        """Extract ZIP file contents"""
        print('Creating temporary folders...')
        try:
            from .zip_handler import handle_zip_file
            handle_zip_file(self.zip_path, self.working_folder)
        except ImportError as e:
            raise FileProcessingError(f"Failed to import zip_handler: {e}")
        except Exception as e:
            raise FileProcessingError(f"Error extracting ZIP file: {str(e)}")
    
    def _list_files(self) -> List[Dict[str, Any]]:
        """List files in the working directory"""
        print('Collecting conversation files...')
        try:
            from list_files import list_files_in_directory
            return list_files_in_directory(self.working_folder)
        except ImportError:
            # Fallback function
            files = []
            for root, dirs, file_names in os.walk(self.working_folder):
                for file_name in file_names:
                    file_path = os.path.join(root, file_name)
                    files.append({
                        'name': file_name,
                        'path': file_path,
                        'size': os.path.getsize(file_path)
                    })
            return files
        except Exception as e:
            raise FileProcessingError(f"Error listing files: {str(e)}")
    
    def _handle_iphone_contact_extraction(self) -> None:
        """Handle iPhone contact extraction if needed"""
        if (self.analysis_data.detected_device == DeviceType.IPHONE.value and 
            not self.analysis_data.whatsapp_contact):
            
            chat_file_path = os.path.join(self.working_folder, "_chat.txt")
            if os.path.exists(chat_file_path):
                contact = self.zip_analyzer.extract_iphone_contact(chat_file_path)
                if contact:
                    print("---WhatsAppContact (iPhone)---")
                    print(contact)
    
    def _process_media(self) -> tuple[Dict[str, str], Dict[str, List[str]]]:
        """Process all media files"""
        self.media_processor = MediaProcessor(self.working_folder)
        return self.media_processor.process_all_media()
    
    def _extract_messages(self, file_list: List[Dict[str, Any]]) -> List[MessageData]:
        """Extract messages from the chat file"""
        print('Processing files and media...')
        
        # Get detected device type
        device_type = self.analysis_data.detected_device or DeviceType.ANDROID.value
        
        if device_type not in (DeviceType.ANDROID.value, DeviceType.IPHONE.value):
            raise DeviceDetectionError("Erro: Não é possível detectar modelo de celular")
        
        # Extract messages
        self.message_extractor = MessageExtractor(self.working_folder)
        return self.message_extractor.extract_messages(
            file_list, 
            device_type, 
            self.analysis_data.whatsapp_contact
        )
    
    def _append_media_to_messages(
        self, 
        messages: List[MessageData], 
        transcriptions: Dict[str, str],
        pdf_images: Dict[str, List[str]]
    ) -> List[MessageData]:
        """Append media files to messages"""
        try:
            # Append transcriptions
            messages = self.media_processor.append_transcriptions(messages)
            
            # Append PDF images
            messages = self.media_processor.append_pdf_images(messages)
            
            return messages
        except Exception as e:
            raise FileProcessingError(f"Error appending media to messages: {str(e)}")
    
    def _save_results(self, messages: List[MessageData]) -> List[MessageData]:
        """Save processing results to files"""
        print('Organizing messages...')
        
        # Save main output
        output_path = os.path.join(self.working_folder, 'output.json')
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(messages, f, ensure_ascii=False, indent=2)
            
            # Read back the results
            with open(output_path, 'r', encoding='utf-8') as f:
                result = json.load(f)
        except Exception as e:
            raise FileProcessingError(f"Error saving or reading results: {str(e)}")
        
        # Save analysis data
        analysis_path = os.path.join(self.working_folder, 'analysis.json')
        try:
            with open(analysis_path, 'w', encoding='utf-8') as f:
                json.dump(self.analysis_data.to_dict(), f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Warning: Could not save analysis data: {str(e)}")
        
        return result
    
    @staticmethod
    def generate_unique_folder_name() -> str:
        """Generate a unique folder name for processing"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:8]
        return f"{timestamp}_processing_{unique_id}"