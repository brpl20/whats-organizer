"""
WhatsApp Processor - Main Application
Refactored and organized WhatsApp conversation processor
"""
import json
import os
import sys
from typing import Dict, Any

# Add both current directory and parent directory to path for local imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, current_dir)
sys.path.insert(0, parent_dir)

from core.conversation_processor import ConversationProcessor
from utils.logging_utils import setup_logging, get_logger
from utils.file_utils import FileUtils
from exceptions.custom_exceptions import WhatsAppProcessorError

class WhatsAppProcessor:
    """Main WhatsApp Processor application class"""
    
    def __init__(self, base_folder: str = "./output/"):
        self.logger = setup_logging()
        self.processor = ConversationProcessor(base_folder)
        self.base_folder = base_folder
    
    def process_zip_file(self, file_path: str, unique_folder_name: str = None) -> Dict[str, Any]:
        """
        Process a WhatsApp ZIP file
        
        Args:
            file_path: Path to the ZIP file to process
            unique_folder_name: Optional unique folder name (will be generated if None)
            
        Returns:
            Processing results dictionary
        """
        if unique_folder_name is None:
            unique_folder_name = ConversationProcessor.generate_unique_folder_name()
        
        self.logger.info(f"Starting processing of file: {file_path}")
        self.logger.info(f"Working folder: {unique_folder_name}")
        self.logger.info("-" * 50)
        
        try:
            # Validate input file
            if not os.path.exists(file_path):
                raise WhatsAppProcessorError(f"File not found: {file_path}")
            
            # Log file size
            file_size_mb = FileUtils.get_file_size_mb(file_path)
            self.logger.info(f"File size: {file_size_mb:.2f} MB")
            
            # Process the conversation
            result = self.processor.process_conversation(file_path, unique_folder_name)
            
            if "Erro" in result:
                self.logger.error(f"❌ ERROR: {result['Erro']}")
                return result
            
            # Log success
            self._log_success_results(result, unique_folder_name)
            return result
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self.logger.error(f"❌ {error_msg}")
            import traceback
            self.logger.error(traceback.format_exc())
            return {"Erro": error_msg}
    
    def _log_success_results(self, result: Dict[str, Any], unique_folder_name: str) -> None:
        """Log success results and preview"""
        self.logger.info("✅ Processing completed successfully!")
        
        messages = result.get('resultado', [])
        self.logger.info(f"📊 Messages processed: {len(messages)}")
        
        analysis = result.get('analise', {})
        if analysis.get('detected_device'):
            self.logger.info(f"📱 Detected device: {analysis['detected_device']}")
        if analysis.get('whatsapp_contact'):
            self.logger.info(f"👤 Contact: {analysis['whatsapp_contact']}")
        
        # Show file path
        output_path = os.path.join(self.base_folder, unique_folder_name, "output.json")
        self.logger.info("\n" + "=" * 50)
        self.logger.info(f"📁 File generated at: {output_path}")
        self.logger.info("=" * 50)
        
        # Show content preview
        if os.path.exists(output_path):
            self._show_preview(output_path)
    
    def _show_preview(self, output_path: str) -> None:
        """Show a preview of the processed content"""
        try:
            self.logger.info("\n📋 CONTENT PREVIEW (first 3 messages):")
            self.logger.info("-" * 50)
            
            data = FileUtils.load_json(output_path)
            for i, msg in enumerate(data[:3], 1):
                self.logger.info(f"\nMessage {i}:")
                self.logger.info(f"  Name: {msg.get('Name', 'N/A')}")
                self.logger.info(f"  Date: {msg.get('Date', 'N/A')} {msg.get('Time', 'N/A')}")
                
                message_text = msg.get('Message', 'N/A')
                if len(message_text) > 100:
                    message_text = message_text[:100] + "..."
                self.logger.info(f"  Message: {message_text}")
                
                if msg.get('FileAttached'):
                    self.logger.info(f"  File: {msg.get('FileAttached')}")
            
            self.logger.info("\n" + "-" * 50)
            self.logger.info(f"💾 To see the complete file, open: {output_path}")
            
        except Exception as e:
            self.logger.warning(f"Could not show preview: {str(e)}")

def main():
    """Main function for running the processor"""
    # File paths for testing
    android_folder = "/home/brpl/code/whats-organizer/tests/android/"
    iphone_folder = "/home/brpl/code/whats-organizer/tests/iphone/"
    
    # Choose test file
    # file_path = android_folder + "teste-audio-curto-uma-imagem.zip"
    # file_path = iphone_folder + "audio-video-docx.zip"
    file_path = android_folder + "teste-audio-curto-uma-imagem.zip"
    
    # Initialize processor
    processor = WhatsAppProcessor()
    
    # Process the file
    result = processor.process_zip_file(file_path)
    
    # Return result for further processing if needed
    return result

if __name__ == "__main__":
    main()