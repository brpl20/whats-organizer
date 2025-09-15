# Pasta Deprecados

Esta pasta contém arquivos que foram substituídos pela nova arquitetura modular do WhatsApp Processor.

## Arquivos Deprecados:

### `process_convo.py`
- **Status:** ❌ Obsoleto
- **Substituído por:** `whatsapp-processor/core/conversation_processor.py` + `api/whatsapp_api.py`
- **Motivo:** Refatoração para arquitetura modular com melhor separação de responsabilidades
- **Funcionalidade:** Processamento principal de conversas WhatsApp via Flask
- **Nova implementação:** Usa o sistema modular com tratamento de exceções robusto

## Não Remover

Estes arquivos são mantidos para:
- 📚 **Referência histórica** do desenvolvimento
- 🔄 **Fallback** em caso de problemas com a nova implementação
- 📖 **Documentação** de como o sistema funcionava antes da refatoração

## Nova Arquitetura

A nova arquitetura está em:
```
whatsapp-processor/     # Sistema modular refatorado
├── core/              # Processamento principal
├── models/            # Modelos de dados
├── utils/             # Utilitários
└── exceptions/        # Tratamento de erros

api/                   # Nova API
└── whatsapp_api.py    # Interface Flask compatível

app_new.py            # Nova aplicação Flask
```

## Data de Migração
- **Criado:** 2025-08-19
- **Motivo:** Reestruturação para código mais limpo e manutenível