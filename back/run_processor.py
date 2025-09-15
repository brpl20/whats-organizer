#!/usr/bin/env python3
"""
Script de execução para o WhatsApp Processor
"""
import sys
import os

# Adicionar o diretório whatsapp-processor ao path
processor_dir = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, processor_dir)

# Importar e executar o main
from main import main

if __name__ == "__main__":
    main()