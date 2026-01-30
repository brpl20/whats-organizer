"""
Configuração centralizada da aplicação
"""
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente uma única vez
load_dotenv(override=True)

class Config:
    """Classe de configuração centralizada"""
    WHISPER = os.getenv("WHISPER")
    WHISPER_GROQ = os.getenv("WHISPER_GROQ")
    WHISPER_LANG = os.getenv("WHISPER_LANG", "pt")

    @classmethod
    def has_whisper_key(cls):
        """Verifica se a chave do Whisper está configurada"""
        return bool(cls.WHISPER)

    @classmethod
    def has_groq_key(cls):
        """Verifica se a chave do Groq está configurada"""
        return bool(cls.WHISPER_GROQ)

# Instância única de configuração
config = Config()