"""
Configuração centralizada da aplicação
"""
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente uma única vez
load_dotenv(override=True)

class Config:
    """Classe de configuração centralizada"""
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Adicione outras configurações conforme necessário
    # DATABASE_URL = os.getenv("DATABASE_URL")
    # DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    @classmethod
    def has_openai_key(cls):
        """Verifica se a chave da OpenAI está configurada"""
        return bool(cls.OPENAI_API_KEY)

# Instância única de configuração
config = Config()