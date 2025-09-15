## Documentação de Componentes em Uso:

O fluxo do código inicia em Main (Main é onde contém todo o código e lógica genérica).

Main: Lógica principal de chat/ Apresentação
    -> Títulos, cabeçalho, container de chat
    -> Mensagem, bolha de mensagem, Mensagem de Mídia
    -> Instruções, Modal de LGPD, Modal de Limitações
    -> Lógica de upload/ gerar chat

UploadButton: Botão de upload de arquivos/ carregando
    -> Lógica de arrastar (drag and drop)
    -> Propaga uma atualização do state de arquivos para o componente pai (notifica upload pronto)


Toast: Notificação
    -> Toast de carregamento (Fazendo requisição)
    -> Toast Personalizável (Ícone e cor)

ChatComponents: Componentes menores do chat
    -> Audio: Contém um elemento html5 de áudio e customizações do chrome
    -> Video: Contém um elemento html5 de vídeos, um pré renderizador de minitura (thumbnail ou thumb), o renderizador serve pra mostrar as minituras quando gera o pdf
    -> Ambos componentes possuem lógica de renderização integrada no playwright para esperar carregar mídias antes de gerar o PDF

SVG: SVGs são adicionados como componentes Svelte puros
    -> PrinterSVG: Ícone da toast gerando PDF
    -> TranscribeSVG: Ícone da toast gerando PDF (transcrevendo áudios)
    -> ErrorSVG: Ícone da toast de Erro
    -> CloseSVG: Ícone de fechar a toast



