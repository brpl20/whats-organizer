"""
New WhatsApp API using the refactored processor
Maintains compatibility with existing frontend while using the new modular system
"""
import os
import sys
import shutil
from typing import Dict, Any, Callable

# Add whatsapp-processor to path
processor_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src')
sys.path.insert(0, processor_dir)

from core.conversation_processor import ConversationProcessor
from utils.file_utils import FileUtils

class WhatsAppAPI:
    """New API class using the refactored processor"""

    def __init__(self, base_folder: str = "./output/"):
        self.base_folder = base_folder
        self.processor = ConversationProcessor(base_folder)

    def process_zip_file(self, file_path: str, notify_callback: Callable[[str], None]) -> Dict[str, Any]:
        """
        Process a WhatsApp ZIP file using the new modular system

        Args:
            file_path: Path to the uploaded ZIP file on disk
            notify_callback: Function to send progress updates

        Returns:
            dict with 'resultado' key (messages list) or 'Erro' key (error string),
            plus '_working_folder' for LGPD cleanup
        """
        try:
            # Generate truly unique folder name with timestamp + UUID
            import uuid
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            unique_id = uuid.uuid4().hex[:8]
            unique_folder_name = f"{timestamp}_processing_{unique_id}"

            # Save file temporarily
            notify_callback('Recebendo Arquivo zip...')
            temp_file_path = self._save_temp_file(file_path, unique_folder_name)

            # Create progress callback wrapper
            progress_callback = self._create_progress_wrapper(notify_callback)

            # Process using new system
            result = self._process_with_new_system(temp_file_path, unique_folder_name, progress_callback)

            # Include working folder path for LGPD cleanup
            working_folder = os.path.join(self.base_folder, unique_folder_name)
            result['_working_folder'] = working_folder

            if "Erro" in result:
                return result

            notify_callback('Processamento Finalizado!')
            return result

        except Exception as e:
            # Handle SecurityError separately to preserve the original message
            if "MALICIOSO" in str(e) or "malicious" in str(e) or "perigosos" in str(e):
                error_msg = str(e)
                notify_callback(f"ARQUIVO PERIGOSO: {error_msg}")
                return {"Erro": error_msg}
            else:
                error_msg = f"Erro inesperado: {str(e)}"
                notify_callback(f"Erro: {error_msg}")
                return {"Erro": error_msg}

    def _save_temp_file(self, file_path: str, unique_folder_name: str) -> str:
        """Copy uploaded file to working directory"""
        temp_dir = os.path.join(self.base_folder, f"temp_{unique_folder_name}")
        FileUtils.ensure_directory_exists(temp_dir)

        temp_file_path = os.path.join(temp_dir, "uploaded.zip")
        shutil.copy2(file_path, temp_file_path)

        return temp_file_path

    def _create_progress_wrapper(self, notify_callback: Callable[[str], None]) -> Callable[[str], None]:
        """Create progress callback that maps new system messages to old system format"""

        progress_mapping = {
            'Copying ZIP file...': 'Recebendo Arquivo zip...',
            'Analyzing ZIP file for security...': 'Analisando arquivo ZIP para seguranca...',
            'Creating temporary folders...': 'Criando Pastas Provisorias...',
            'Collecting conversation files...': 'Coletando Arquivos da Conversa...',
            'Converting audio and transcribing...': 'Convertendo MP3 e Transcrevendo Audios...',
            'Processing PDFs and Office documents...': 'Trabalhando com PDFs e Office...',
            'Processing files and media...': 'Processando Arquivos e Midia...',
            'Organizing messages...': 'Organizando Mensagens...',
            'Android detected!': 'Android detectado!',
            'iPhone detected!': 'iPhone detectado!',
        }

        def wrapped_callback(message: str) -> None:
            mapped_message = progress_mapping.get(message, message)
            notify_callback(mapped_message)

        return wrapped_callback

    def _process_with_new_system(self, file_path: str, unique_folder_name: str, progress_callback: Callable[[str], None]) -> Dict[str, Any]:
        """Process file using the new modular system"""

        # Intercept and map the internal progress messages
        original_print = __builtins__.get('print', print)

        def progress_print(*args, **kwargs):
            message = ' '.join(str(arg) for arg in args)

            # Map specific progress messages
            if any(keyword in message for keyword in [
                'Copying', 'Analyzing', 'Creating', 'Collecting',
                'Converting', 'Processing', 'Organizing', 'detected'
            ]):
                progress_callback(message)

            # Still call original print for logging
            original_print(*args, **kwargs)

        # Temporarily replace print
        __builtins__['print'] = progress_print if isinstance(__builtins__, dict) else setattr(__builtins__, 'print', progress_print)

        try:
            # Process using new system
            result = self.processor.process_conversation(file_path, unique_folder_name)
            return result

        finally:
            # Restore original print
            if isinstance(__builtins__, dict):
                __builtins__['print'] = original_print
            else:
                setattr(__builtins__, 'print', original_print)

            # Clean up temp file
            try:
                temp_dir = os.path.dirname(file_path)
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
            except Exception as e:
                print(f"Warning: Could not clean temp file: {e}")

# Function to maintain compatibility with existing app.py
def create_whatsapp_api(base_folder: str = "./zip_tests/") -> WhatsAppAPI:
    """Factory function to create WhatsApp API instance"""
    return WhatsAppAPI(base_folder)
