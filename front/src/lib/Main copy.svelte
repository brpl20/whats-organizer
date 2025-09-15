<script>
  import { onMount } from 'svelte';
  import { fade } from 'svelte/transition';
  import JSZip from 'jszip';
  import mammoth from 'mammoth';
  import { browser } from '$app/environment';
  import { PUBLIC_API_URL } from '$env/static/public';


  let fileInput;
  let result = null;
  let isLoading = false;
  let error = null;
  let showLimitacoesModal = false;
  let showLGPDModal = false;
  let messages = [];

  function toggleLimitacoesModal() {
    showLimitacoesModal = !showLimitacoesModal;
  }

  function toggleLGPDModal() {
    showLGPDModal = !showLGPDModal;
  }

  async function processZipFile(file) {
    const zip = new JSZip();
    const contents = await zip.loadAsync(file);
    
    for (let [filename, zipEntry] of Object.entries(contents.files)) {
      const arrayBuffer = await zipEntry.async('arraybuffer');
      const blob = new Blob([arrayBuffer], { type: getFileType(filename) });
      const url = URL.createObjectURL(blob);
      
      messages = await Promise.all(messages.map(async (msg) => {
        if (msg.FileAttached === filename) {
          const fileInfo = await getFileInfo(blob, filename);
          return { ...msg, FileURL: url, ...fileInfo };
        }
        return msg;
      }));
    }
  }

  function getFileType(filename) {
    const ext = filename.split('.').pop().toLowerCase();
    switch (ext) {
      case 'pdf': return 'application/pdf';
      case 'docx': return 'application/vnd.openxmlformats-officedocument.wordprocessingml.document';
      case 'jpg':
      case 'jpeg': return 'image/jpeg';
      case 'png': return 'image/png';
      case 'gif': return 'image/gif';
      case 'mp4': return 'video/mp4';
      case 'opus': return 'audio/opus';
      default: return 'application/octet-stream';
    }
  }

  async function getFileInfo(blob, filename) {
    const ext = filename.split('.').pop().toLowerCase();
    switch (ext) {
      case 'pdf':
        return { type: 'pdf' };
      case 'docx':
        return await getDocxInfo(blob);
      case 'jpg':
      case 'jpeg':
      case 'png':
      case 'gif':
        return await getImageInfo(blob);
      case 'mp4':
        return await getVideoInfo(blob);
      case 'opus':
        return { type: 'audio' };
      default:
        return {};
    }
  }

  async function getDocxInfo(blob) {
    const arrayBuffer = await blob.arrayBuffer();
    const result = await mammoth.convertToHtml({ arrayBuffer });
    const text = result.value;
    const pages = text.split('\n\n').slice(0, 6);
    return { type: 'docx', pages };
  }

  async function getImageInfo(blob) {
    return new Promise((resolve) => {
      const img = new Image();
      img.onload = () => resolve({ type: 'image', width: img.width, height: img.height });
      img.src = URL.createObjectURL(blob);
    });
  }

  async function getVideoInfo(blob) {
    return new Promise((resolve) => {
      const video = document.createElement('video');
      video.onloadedmetadata = () => {
        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
        const thumbnail = canvas.toDataURL();
        resolve({ type: 'video', duration: video.duration, thumbnail });
      };
      video.src = URL.createObjectURL(blob);
    });
  }

  async function handleSubmit() {
    if (!fileInput.files[0]) {
      error = "Por favor selecione um arquivo zip antes (confira se possui a extensão correta).";
      return;
    }

    const file = fileInput.files[0];
    if (!file.name.endsWith('.zip')) {
      error = "Por favor selecione um arquivo.";
      return;
    }

    error = null;
    isLoading = true;
    result = null;

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${PUBLIC_API_URL}/process`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      result = await response.json();
      // Check if the response contains an error
      if (Array.isArray(result) && result.length > 0 && result[0].ERRO) {
        error = result[0].ERRO; // Set the error message to be displayed
      } else {
        messages = result;
        await processZipFile(file);
      }
    } catch (e) {
      console.error("Houve um erro ao processar o arquivo:", e);
      error = "Houve um erro ao processar o arquivo. Por favor tente .";
    } finally {
      isLoading = false;
    }
  }

  function isAudioFile(filename) {
    return filename && filename.endsWith('.opus');
  }

  function getFileName(path) {
    return path.split('/').pop();
  }

  function editTranscription(message) {
    // Implement transcription editing logic here
    console.log('Edit transcription for:', message);
  }

  onMount(() => {
    if (browser) {
      // Any client-side initialization code can go here
    }
  });
</script>

<svelte:head>
  <title>WhatsOrganizer</title>
</svelte:head>

<main>
  <h1>WhatsOrganizer</h1>
  
  <p class="subtitle">
    Organize suas conversas de WhatsApp<br>
    e transcreva áudios de forma rápida e<br>
    segura de uma única vez
  </p>
  
  <div>
    <input type="file" bind:this={fileInput} accept=".zip" />
    <button on:click={handleSubmit} disabled={isLoading}>
      {isLoading ? 'Processing...' : 'Send'}
    </button>
  </div>
  
  {#if error}
    <p class="error">{error}</p>
  {/if}

  {#if messages.length > 0}
    <div class="chat-container">
      {#each messages as message}
        <div class="message-wrapper {message.ID === 1 ? 'left' : 'right'}">
          <div class="message-bubble">
            <div class="message-header">
              <span class="message-name">{message.Name}</span>
              <span class="message-time">{message.Time}</span>
            </div>
            
            {#if message.FileAttached}
              {#if message.type === 'pdf'}
                <div class="file-attachment">
                  <img src="/pdf-icon.png" alt="PDF" class="file-icon" />
                  <span>{message.FileAttached}</span>
                </div>
              {:else if message.type === 'docx'}
                <div class="docx-preview">
                  {#each message.pages as page, i}
                    <p>{page}</p>
                  {/each}
                  {#if message.pages.length === 6}
                    <span class="more-pages">...</span>
                    <p>Arquivo maior que seis páginas, consulte o original</p>
                  {/if}
                </div>
              {:else if message.type === 'image'}
                <img src={message.FileURL} alt="Image" class="image-preview" />
              {:else if message.type === 'video'}
                <div class="video-preview">
                  <img src={message.thumbnail} alt="Video thumbnail" />
                  <video controls src={message.FileURL}></video>
                </div>
              {:else if isAudioFile(message.FileAttached)}
                <div class="audio-message">
                  <div class="audio-filename">{getFileName(message.FileAttached)}</div>
                  <audio controls src={message.FileURL}></audio>
                  {#if message.AudioTranscription}
                    <div class="transcription">
                      {message.AudioTranscription}
                    </div>
                  {/if}
                </div>
              {:else}
                <div class="file-attachment">
                  <img src="/file-icon.png" alt="File" class="file-icon" />
                  <span>{message.FileAttached}</span>
                </div>
              {/if}
            {:else}
              <p class="message-text">{message.Message}</p>
            {/if}
          </div>
          <div class="message-date">{message.Date}</div>
        </div>
      {/each}
    </div>
  {/if}

  <p class="instructions">
    Faça o upload do seu arquivo exportado do WhatsApp<br>
    ele estará no formato .zip, confira como fazer:
  </p>

  <div class="icons">
    <span class="icon">🍎</span>
    <span class="icon">🤖</span>
  </div>

  <div class="buttons">
    <button class="secondary" on:click={toggleLimitacoesModal}>Limitações</button>
    <button class="secondary" on:click={toggleLGPDModal}>LGPD</button>
  </div>

  <footer>
    2024 por ProcStudio e Bruno Pellizzetti
  </footer>
</main>

{#if showLimitacoesModal}
  <div class="modal-backdrop" on:click={toggleLimitacoesModal}>
    <div class="modal" transition:fade on:click|stopPropagation>
      <h2>Limitações</h2>
      <ul>
        <li>Grupos não suportados</li>
        <li>Tamanho máximo dos arquivos: 40 Mb</li>
        <li>Não confere garantia de autenticidade</li>
      </ul>
      <button on:click={toggleLimitacoesModal}>Fechar</button>
    </div>
  </div>
{/if}

{#if showLGPDModal}
  <div class="modal-backdrop" on:click={toggleLGPDModal}>
    <div class="modal" transition:fade on:click|stopPropagation>
      <h2>LGPD</h2>
      <p>Não coletamos nenhum dado e todos os arquivos são totalmente destruídos após as etapas do organizador serem concluídas.</p>
      <button on:click={toggleLGPDModal}>Fechar</button>
    </div>
  </div>
{/if}

<style>
    main {
    font-family: Arial, sans-serif;
    max-width: 600px;
    margin: 0 auto;
    padding: 20px;
    text-align: center;
    background-color: #58F1C4;
    color: #1c1c1c;
    border-radius: 10px;
  }

  h1 {
    font-size: 2.5em;
    margin-bottom: 10px;
    font-family: 'Alfa Slab One', system-ui;
    text-shadow: 0 4px 4px rgba(0, 0, 0, 0.25);
    color: #005C4B;
  }

  .subtitle, .instructions {
    margin-bottom: 20px;
    color: #019D80
  }

  .input-group {
    display: flex;
    margin-bottom: 20px;
  }

  input[type="file"] {
    flex-grow: 1;
    padding: 10px;
    border: none;
    border-radius: 5px 0 0 5px;
    background-color: white;
  }

  button {
    padding: 10px 20px;
    border: none;
    border-radius: 0 5px 5px 0;
    background-color: #1c1c1c;
    color: white;
    cursor: pointer;
  }

  .icons {
    font-size: 2em;
    margin-bottom: 20px;
  }

  .icon {
    margin: 0 10px;
  }

  .buttons {
    display: flex;
    justify-content: center;
    gap: 20px;
    margin-bottom: 20px;
  }

  .error {
    color: red;
  }

  .secondary {
    background-color: transparent;
    border: 2px solid #1c1c1c;
    color: #1c1c1c;
    border-radius: 5px;
  }

  footer {
    font-size: 0.8em;
    margin-top: 20px;
  }

  .modal-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .modal {
    background-color: white;
    padding: 20px;
    border-radius: 5px;
    max-width: 400px;
    text-align: left;
  }

  .modal h2 {
    margin-top: 0;
  }

  .modal button {
    margin-top: 10px;
    background-color: #00ffa6;
    color: #1c1c1c;
    border-radius: 5px;
  }

  .modal ul {
    padding-left: 20px;
  }

  .chat-container {
    max-width: 100%;
    margin: 20px 0;
    padding: 20px;
    background-color: #e5ddd5;
    border-radius: 10px;
    text-align: left;
  }

  .message-wrapper {
    display: flex;
    flex-direction: column;
    margin-bottom: 10px;
  }

  .left {
    align-items: flex-start;
  }

  .right {
    align-items: flex-end;
  }

  .message-bubble {
    max-width: 70%;
    padding: 10px;
    border-radius: 10px;
    background-color: white;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  }

  .left .message-bubble {
    background-color: #ffffff;
  }

  .right .message-bubble {
    background-color: #dcf8c6;
  }

  .message-header {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 5px;
    font-size: 0.8em;
  }

  .message-name {
    font-weight: bold;
  }

  .message-time {
    color: #999;
    padding-left: 0.3em;
  }

  .message-text {
    margin: 0;
    word-break: break-word;
  }

  .message-date {
    font-size: 0.7em;
    color: #999;
    margin-top: 5px;
    padding-left: 1em;
    padding-right: 1em;
    display: inline-block;
  }

  .audio-message audio {
    width: 100%;
    border-radius: 20px;
  }

  .audio-filename {
    font-size: 0.8em;
    color: #666;
    margin-bottom: 5px;
  }

  .transcription {
    margin-top: 5px;
    font-style: italic;
    color: #666;
  }

  .file-attachment {
    display: flex;
    align-items: center;
  }

  .file-icon {
    width: 30px;
    height: 30px;
    margin-right: 10px;
  }

  .pdf-preview, .docx-preview {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
  }

  .pdf-preview img, .docx-preview p {
    width: calc(33% - 10px);
    object-fit: cover;
    border: 1px solid #ccc;
  }

  .more-pages {
    font-size: 24px;
    font-weight: bold;
  }

  .image-preview {
    max-width: 100%;
    height: auto;
  }

  .video-preview {
    position: relative;
  }

  .video-preview img {
    width: 100%;
    height: auto;
  }

  .video-preview video {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
  }

  .edit-transcription {
    background: none;
    border: none;
    cursor: pointer;
    padding: 0;
    margin-left: 5px;
  }


  /* ... (styles remain the same as in the previous version) */
</style>