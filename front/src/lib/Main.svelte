<script>
	import { fade } from 'svelte/transition';
	import { PUBLIC_API_URL, PUBLIC_NODE_ENV, PUBLIC_MAX_UPLOAD_MB } from '$env/static/public';
	import UploadButton from './UploadButton.svelte';
	import { onDestroy } from 'svelte';
	import Video from './ChatComponents/Video.svelte';
	import Audio from './ChatComponents/Audio.svelte';
	import Toast from './Toast.svelte';
	import TranscribeSvg from './TranscribeSvg.svelte';
	import PrintSvg from './PrinterSvg.svelte';
	import ErrorSvg from './ErrorSvg.svelte';
	import { MessageCircle, FileText, X, Download, AlertTriangle, Shield, Info } from 'lucide-svelte';

	/**
	 * @typedef {import('./types/toast.type.js').ToastTypes} ToastTypes
	 * @typedef {import('./types/toast.type.js').ToastProps} ToastProps
	 * @typedef {import('jszip')=} JsZip
	 * @typedef {import('mammoth')=} Mammoth
	 * @typedef {import('socket.io-client').default=} SocketIo
	 * @typedef {import('socket.io-client').Socket<DefaultEventsMap, DefaultEventsMap>=} SocketType
	 */

	const prod = (PUBLIC_NODE_ENV || '').toLowerCase() in ['prod', 'production'];

	/** Timeout caso o socketio não consiga conectar */
	const socketConnTimeout = 5000;

	const uuid = crypto.randomUUID();

	/** @type {HTMLDivElement=}*/
	let chatContainer = null;

	/** @type {string=}*/
	let showLimitacoesModal = false;
	let showLGPDModal = false;
	let showMediaModal = false;

	/**
	 * @typedef {object} MediaModalData
	 * @property {string} type - 'image' | 'pdf'
	 * @property {string} src - URL da mídia
	 * @property {string} filename - Nome do arquivo
	 * @property {string[]=} links - Para PDFs com múltiplas páginas
	 */
	/** @type {MediaModalData=} */
	let currentMedia = null;

	/**
	 * @typedef {object} ApiResult
	 * @property {string} Date
	 * @property {string|false} FileAttached
	 * @property {number} ID
	 * @property {string} Message
	 * @property {string} Name
	 * @property {string} Time
	 * @property {boolean} IsApple
	 * @property {string=} ERRO
	 */
	/**
	 * @typedef {object} ApiError
	 * @property {string=} Erro
	 */
	/** @type {(ApiResult[]|ApiError)=} */
	let result = null;
	/**
	 * @typedef {object} Message
	 * @property {string} Date
	 * @property {string|false} FileAttached
	 * @property {number} ID
	 * @property {string} Message
	 * @property {string} Name
	 * @property {string} Time
	 * @property {string=} FileURL
	 * @property {string=} type
	 * @property {number=} width
	 * @property {number=} height
	 * @property {number=} duration
	 * @property {string=} thumbnail
	 * @property {string[]} links
	 */
	/** @type {Message[]} */
	let messages = [];
	/** @type {FileList=} */
	let files = null;
	// maioria é android
	let isApple = false;

	/**
	 * @typedef {Pick<ToastProps, 'text' | 'onClose'> & {type: Exclude<ToastTypes, 'all'>}} ToastType
	 * @type {ToastType}
	 */
	let toast = {
		text: null,
		type: 'transcribe',
		isSecurityError: false
	};
	const loading = !!toast.text && toast.type == 'transcribe';
	const printLoading = toast.type === 'print' && !loading;

	let uploadDisabled = false;

	// Variável para controlar se o processamento está desabilitado
	$: isProcessingDisabled = messages?.length > 0 || uploadDisabled;

	/** @type {Record<ToastTypes, ToastProps>} */
	const toastMap = {
		transcribe: {
			svg: TranscribeSvg
		},
		print: {
			svg: PrintSvg
		},
		error: {
			svg: ErrorSvg,
			error: true
		}
	};

	/** @type {Record<ToastTypes, ToastProps>} */
	$: toastProps = {
		...toastMap[toast.type],
		text: toast.text,
		closed: !toast.text,
		onClose: toast.onClose,
		isSecurityError: toast.isSecurityError
	};

	/** @param {ToastTypes} newType */
	const removeToast = (newType) =>
		(toast = { ...toast, text: null, isSecurityError: false, ...(newType && { type: newType }) });

	/** @param {CustomEvent<FileList>} event */
	const updateFiles = (event) => {
		files = event.detail;
		// Limpar mensagens quando novo arquivo for selecionado
		if (files?.length > 0) {
			messages = [];
			result = null;
		}
	};

	/** Optimize import on-demand for heavy libs */
	/** @type {JsZip} */
	let JSZip = null;
	/** @type {Mammoth} */
	let mammoth = null;
	/** @type {SocketIo} */
	let io = null;

	/** @type {SocketType} */
	let socket = null;

	onDestroy(() => (prod ? socket?.disconnect?.() : () => undefined));

	const toggleLimitacoesModal = () => (showLimitacoesModal = !showLimitacoesModal);

	const toggleLGPDModal = () => (showLGPDModal = !showLGPDModal);

	const toggleMediaModal = () => {
		showMediaModal = !showMediaModal;
		if (!showMediaModal) {
			currentMedia = null;
		}
	};

	/**
	 * @param {string} src
	 * @param {string} filename
	 * @param {string} type
	 * @param {string[]=} links
	 */
	const openMediaModal = (src, filename, type, links = null) => {
		currentMedia = { src, filename, type, links };
		showMediaModal = true;
	};

	/** @param {[string, string, Blob][]} urls */
	const processMessages = async (urls) =>
		(async () => {
			const fileMap = new Map(urls.map(([url, filename, blob]) => [filename, { url, blob }]));

			messages = await Promise.all(
				messages.map(async (msg) => {
					const match = fileMap.get(msg.FileAttached);
					if (match) {
						const fileInfo = await getFileInfo(match.blob, msg.FileAttached);
						return { ...msg, FileURL: match.url, ...fileInfo };
					}
					return msg;
				})
			);

			removeToast('print');
		})();

	/** @param {File} file */
	async function processZipFile(file) {
		JSZip ??= (await import('jszip')).default;
		const zip = new JSZip();
		const contents = await zip.loadAsync(file);

		const urls = Object.entries(contents.files).map(async ([filename, zipEntry]) => {
			const arrayBuffer = await zipEntry.async('arraybuffer');
			const blob = new Blob([arrayBuffer], { type: getFileType(filename) });
			const url = URL.createObjectURL(blob);
			return [url, filename, blob];
		});

		return Promise.all(urls);
	}

	const verifyFileErr = 'Erro ao Processar, Verifique o Arquivo.';

	/** @param {File} file */
	const processConversation = (file) => {
		processZipFile(file)
			.then((urls) => processMessages(urls))
			.catch((e) => {
				toast = {
					type: 'error',
					text: verifyFileErr,
					isSecurityError: false
				};
				console.error(e);
			});
	};

	const getExt = (/** @type {string} */ filename) => filename.split('.').pop().toLowerCase();

	/** @param {string} filename */
	function getFileType(filename) {
		const ext = getExt(filename);
		switch (ext) {
			case 'pdf':
				return 'application/pdf';
			case 'docx':
			case 'docm':
			case 'doc':
			case 'odt':
				return 'application/vnd.openxmlformats-officedocument.wordprocessingml.document';
			case 'pptx':
			case 'ppt':
			case 'odp':
				return 'application/vnd.openxmlformats-officedocument.presentationml.presentation';
			case 'xlsx':
			case 'xls':
			case 'ods':
				return 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
			case 'jpg':
			case 'jpeg':
				return 'image/jpeg';
			case 'png':
				return 'image/png';
			case 'gif':
				return 'image/gif';
			case 'mp4':
				return 'video/mp4';
			case 'opus':
				return 'audio/opus';
			default:
				return 'application/octet-stream';
		}
	}

	/**
	 * @param {Blob} blob
	 * @param {string} filename
	 */
	async function getFileInfo(blob, filename) {
		const ext = getExt(filename);
		switch (ext) {
			case 'pdf':
				return { type: 'pdf' };
			case 'docx':
			case 'docm': // docx + macros enabled
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

	/** @param {Blob} blob */
	async function getDocxInfo(blob) {
		const arrayBuffer = await blob.arrayBuffer();
		mammoth ??= await import('mammoth');
		const htmlResult = await mammoth.convertToHtml({ arrayBuffer });
		const text = htmlResult.value;
		const pages = text.split('\n\n').slice(0, 6);
		return { type: 'docx', pages };
	}

	/** @param {Blob} blob */
	const blobToBase64Url = async (blob) =>
		new Promise((resolve, reject) => {
			const reader = new FileReader();
			reader.onload = (_) => resolve(reader.result);
			reader.onerror = (e) => reject(e);
			reader.readAsDataURL(blob);
		});

	/** @param {Blob} blob */
	const getImageInfo = async (blob) =>
		new Promise((resolve) => {
			const img = new Image();
			img.onload = () => resolve({ type: 'image', width: img.width, height: img.height });
			img.src = URL.createObjectURL(blob);
		});

	/** @param {Blob} blob */
	const getVideoInfo = async (blob) =>
		new Promise((resolve) => {
			const video = document.createElement('video');
			video.src = URL.createObjectURL(blob);
			video.onloadedmetadata = () => {
				resolve({ type: 'video', duration: video.duration });
			};
		});

	async function connectSocket() {
		if (!prod) return;
		/**
		 * Socket.active, if socket still retrying to connect
		 * Socket.connected if the socket is currently connected
		 */
		if (socket?.connected) return;

		io ??= (await import('socket.io-client')).default;
		socket ??= io(PUBLIC_API_URL, {
			reconnectionAttempts: 5,
			transports: ['websocket', 'polling', 'webtransport'],
			timeout: socketConnTimeout,
			query: `uid=${uuid}`
		});

		/** @type {Promise<void>} */
		const connect = new Promise((resolve, _) => socket.on('connect', resolve));
		/** @type {Promise<void>} */
		const timeout = new Promise((_, reject) =>
			setTimeout(() => reject(new Error('Connection timed out')), socketConnTimeout)
		);

		Promise.race([connect, timeout]).catch((e) => {
			console.error(e);
			socket = null;
		});

		socket.on('Smessage', (data) => {
			if (!data?.data) return;
			toast = { ...toast, text: data.data };
		});
	}

	/** @param {SubmitEvent} ev */
	async function handleSubmit(ev) {
		uploadDisabled = true;
		if (isProcessingDisabled) {
			toast = {
				type: 'error',
				text: 'Conversa já processada. Selecione um novo arquivo para processar novamente.',
				isSecurityError: false
			};
			return;
		}
		try {
			ev.preventDefault();

			/** @type { { target: {elements: HTMLCollection & HTMLInputElement } } */
			const { target } = ev;
			const elements = target.elements;
			const fileInput = elements?.[1];
			const files = /** @type {FileList} */ (fileInput.files);

			if (!files?.length) {
				toast = {
					type: 'error',
					text: 'Por favor selecione um arquivo zip antes.',
					isSecurityError: false
				};
				return;
			}

			const file = files[0];
			if (!file.name.endsWith('.zip')) {
				toast = {
					type: 'error',
					text: 'Por favor confira a extensão do arquivo (.zip)',
					isSecurityError: false
				};
				return;
			}

			messages = null;
			result = null;
			toast = {
				text: 'Iniciando Processamento',
				type: 'transcribe',
				isSecurityError: false
			};

			connectSocket();

			const formData = new FormData();
			formData.append('file', file);

			const response = await fetch(`${PUBLIC_API_URL}/process?uid=${uuid}`, {
				method: 'POST',
				body: formData
			}).catch((e) => {
				console.error(e);
				toast = {
					type: 'error',
					text: 'Erro ao Enviar o Arquivo, Verifique Sua Conexão.',
					isSecurityError: false
				};
			});
			if (!response) return;

			if (!response.ok) {
				// Try to get error message from response
				try {
					const errorData = await response.json();
					if (errorData.Erro) {
						// Check if it's a security error
						if (
							errorData.Erro.includes('MALICIOSO') ||
							errorData.Erro.includes('malicious') ||
							errorData.Erro.includes('perigosos')
						) {
							toast = {
								type: 'error',
								text: `⚠️ ARQUIVO PERIGOSO DETECTADO!\n\n${errorData.Erro}\n\nPor favor, verifique o conteúdo do arquivo ZIP e remova quaisquer arquivos suspeitos antes de tentar novamente.`,
								isSecurityError: true
							};
						} else {
							toast = { type: 'error', text: errorData.Erro, isSecurityError: false };
						}
					} else {
						toast = { type: 'error', text: verifyFileErr, isSecurityError: false };
					}
				} catch (e) {
					toast = { type: 'error', text: verifyFileErr, isSecurityError: false };
				}
				console.error(`HTTP error! status: ${response.status}`);
				return;
			}

			result = await response.json();
			if (Array.isArray(result) && result.length > 0 && result[0].ERRO) {
				toast = { type: 'error', text: result[0].ERRO, isSecurityError: false };
				return;
			} // else
			if (!Array.isArray(result) && result.Erro) {
				// Check if it's a security error
				if (
					result.Erro.includes('MALICIOSO') ||
					result.Erro.includes('malicious') ||
					result.Erro.includes('perigosos')
				) {
					toast = {
						type: 'error',
						text: `⚠️ ARQUIVO PERIGOSO DETECTADO!\n\n${result.Erro}\n\nPor favor, verifique o conteúdo do arquivo ZIP e remova quaisquer arquivos suspeitos antes de tentar novamente.`,
						isSecurityError: true
					};
				} else {
					toast = { type: 'error', text: result.Erro, isSecurityError: false };
				}
				return;
			}
			messages = result;
			isApple = messages?.[0]?.IsApple;
		
			processConversation(file);
		} catch (e) {
			throw e;
		} finally {
			uploadDisabled = false;
		}
	}

	/**
	 * Cria um arquivo zip com messages json para o back imprimir
	 * @param {File} file
	 * @return {Promise<File>}
	 */
	const addMessagesJson = async (file) => {
		JSZip ??= (await import('jszip')).default;
		const zip = new JSZip();
		const contents = await zip.loadAsync(file);
		contents.file('whats_organizer/messages.json', JSON.stringify(messages));
		const updatedFile = await zip.generateAsync({ type: 'blob' });
		return new File([updatedFile], file.name, { type: file.type });
	};

	/**
	 * Cria um arquivo zip com messages json para o back imprimir
	 * @param {File} file
	 * @return {Promise<Message[]>}
	 */
	const extractMessagesJson = async (file) => {
		JSZip ??= (await import('jszip')).default;
		const zip = new JSZip();
		const contents = await zip.loadAsync(file);

		const msgFile = contents.files['whats_organizer/messages.json'];
		return JSON.parse(await msgFile.async('text'));
	};

	async function generatePDF() {
		if (!chatContainer) {
			console.error('Chat container not found');
			toast = { type: 'error', text: 'Não há chat para imprimir', isSecurityError: false };
			return;
		}
		toast = {
			text: 'Iniciando Impressão',
			type: 'print',
			isSecurityError: false
		};
		connectSocket();

		try {
			const formData = new FormData();
			const zipFile = files[0];
			const fileWithMessages = await addMessagesJson(zipFile);

			formData.append('file', fileWithMessages);

			const response = await fetch(`${PUBLIC_API_URL}/download-pdf`, {
				method: 'POST',
				body: formData
			});

			if (!response.ok) {
				toast = { type: 'error', text: 'Erro ao gerar o PDF', isSecurityError: false };
				console.error(error, await response.text());
				return;
			}

			const blob = await response.blob();
			const url = URL.createObjectURL(blob);

			const a = document.createElement('a');
			a.href = url;
			a.download = 'chat.pdf';
			document.body.appendChild(a);
			a.click();
			document.body.removeChild(a);

			URL.revokeObjectURL(url);

			removeToast();
		} catch (e) {
			toast = { type: 'error', text: 'Erro ao Processar Requisição', isSecurityError: false };
			console.error(error, e);
		}
	}

	/** @param {SubmitEvent} ev */
	const handleMessageInjection = (ev) => {
		/** @type { { target: HTMLInputElement } } */
		const { target } = ev;
		const { value } = target || {};
		if (!value) return;
		messages = JSON.parse(value);
	};

	/**
	 * @param {string} filename
	 * @param {string} ext
	 * @returns {boolean}
	 */
	const isFile = (filename, ext) => filename?.endsWith?.(`.${ext}`);

	/** @param {string} filename */
	const isAudioFile = (filename) => isFile(filename, 'opus');

	/** @param {string} filename */
	const isVideoFile = (filename) => isFile(filename, 'mp4');

	/**
	 * @param {string} filename
	 * @param {string} ext
	 */
	const extIncludes = (filename, ext) => filename.toLowerCase().includes(`.${ext}`);

	/**
	 * @param {string} filename
	 * @param {string[]} files
	 */
	const isInFiles = (filename, files) => files.some((ext) => extIncludes(filename, ext));

	/** @param {string} filename */
	const isImgFile = (filename) => isInFiles(filename, ['jpg', 'jpeg', 'png']);

	/** @param {string} filename */
	const isWordFile = (filename) => isInFiles(filename, ['docx', 'docm']);

	/** @param {string} path */
	const getFileName = (path) => path.split('/').pop();

	/**
	 * Função utilizada pelo backend, pra injetar a conversa e gerar o PDF
	 * em um navegador simulado que roda no servidor (playwright)
	 * @param {Event & {currentTarget: EventTarget & HTMLInputElement}} e
	 */
	const handleBackendFileInjection = (e) => {
		/** @type { { target: HTMLInputElement } } */
		const { target } = e;
		const evFiles = target.files;
		/** @type {File} */
		const injectedFile = evFiles[0];
		extractMessagesJson(injectedFile).then((m) => (messages = m));
		processConversation(injectedFile);
	};

	/**
	 * Pega o lado do chat baseado em dispositivo (Apple/ Android)
	 * @param {boolean} isApple
	 */
	const getSideByDevice = (isApple) => (isApple ? ['left', 'right'] : ['right', 'left']);

	/**
	 * Formatar o tempo para remover segundos
	 * @param {string} time
	 */
	const formatTime = (time) => {
		if (!time) return '';
		// Remove segundos se existir (formato HH:MM:SS -> HH:MM)
		const parts = time.split(':');
		if (parts.length === 3) {
			return `${parts[0]}:${parts[1]}`;
		}
		return time;
	};
</script>

<!-- Toast customizado para erros de segurança -->
{#if toast.text}
	<div
		class="fixed top-4 left-1/2 transform -translate-x-1/2 z-50 transition-all duration-300 ease-in-out"
		transition:fade={{ duration: 300 }}
	>
		<div
			class="bg-white rounded-xl shadow-2xl border border-gray-200 overflow-hidden
			{toast.isSecurityError ? 'max-w-2xl w-[90vw] sm:w-auto' : 'max-w-md'}"
		>
			<!-- Header do Toast -->
			<div
				class="flex items-center justify-between {toast.isSecurityError
					? 'p-6'
					: 'p-4'} border-b border-gray-100"
			>
				<div class="flex items-center space-x-3">
					<div class="flex-shrink-0">
						{#if toast.type === 'error'}
							<div class="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center">
								<ErrorSvg class="w-5 h-5 text-red-600" />
							</div>
						{:else if toast.type === 'transcribe'}
							<div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
								<TranscribeSvg class="w-5 h-5 text-blue-600" />
							</div>
						{:else if toast.type === 'print'}
							<div class="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
								<PrintSvg class="w-5 h-5 text-green-600" />
							</div>
						{/if}
					</div>
					<div class="min-w-0 flex-1">
						<h4 class="text-sm font-semibold text-gray-900">
							{#if toast.type === 'error'}
								{toast.isSecurityError ? 'Alerta de Segurança' : 'Erro'}
							{:else if toast.type === 'transcribe'}
								Processando
							{:else if toast.type === 'print'}
								Gerando PDF
							{/if}
						</h4>
					</div>
				</div>
				<button
					on:click={() => removeToast()}
					class="flex-shrink-0 p-1 hover:bg-gray-100 rounded-lg transition-colors"
					title="Fechar"
				>
					<X class="w-4 h-4 text-gray-500" />
				</button>
			</div>

			<!-- Conteúdo do Toast -->
			<div class={toast.isSecurityError ? 'p-6 pt-4' : 'p-4'}>
				<div class="text-sm text-gray-700 leading-relaxed whitespace-pre-line">
					{toast.text}
				</div>

				{#if toast.type === 'transcribe' || toast.type === 'print'}
					<div class="mt-4 flex items-center space-x-2">
						<div
							class="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"
						></div>
						<span class="text-xs text-gray-500">Aguarde...</span>
					</div>
				{/if}
			</div>
		</div>
	</div>
{/if}

<main
	class="min-h-screen bg-gradient-to-br from-emerald-400 via-teal-500 to-blue-600 relative overflow-hidden"
>
	<!-- Fundo decorativo -->
	<div class="absolute inset-0 bg-black/5"></div>
	<div class="absolute top-20 left-10 w-72 h-72 bg-white/10 rounded-full blur-3xl"></div>
	<div class="absolute bottom-20 right-10 w-96 h-96 bg-emerald-300/20 rounded-full blur-3xl"></div>

	<div class="relative z-10 container mx-auto px-4 py-12">
		<!-- Header -->
		<div class="text-center mb-16 animate-fade-in">
			<div class="flex justify-center items-center mb-6">
				<div class="bg-white/20 backdrop-blur-md rounded-2xl p-4 shadow-2xl border border-white/30">
					<MessageCircle class="w-12 h-12 text-white" />
				</div>
			</div>
			<h1 class="text-5xl md:text-6xl font-bold text-white mb-6 tracking-tight">WhatsOrganizer</h1>
			<p class="text-xl md:text-2xl text-white/90 max-w-2xl mx-auto leading-relaxed font-light">
				Organize suas conversas de WhatsApp e transcreva áudios de forma rápida e segura
			</p>
		</div>

		<!-- Upload Card -->
		<div class="max-w-2xl mx-auto mb-12">
			<div class="">
				<form class="file-zip space-y-6" on:submit={handleSubmit} data-testid="file-upload-form">
					<UploadButton on:update={updateFiles} {loading} disabled={isProcessingDisabled} />

					<!-- Indicador de status do processamento -->
					{#if isProcessingDisabled}
						<div class="bg-green-100 border border-green-300 rounded-xl p-4 text-center">
							<div class="flex items-center justify-center space-x-2">
								<div class="w-5 h-5 bg-green-500 rounded-full flex items-center justify-center">
									<svg class="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
										<path
											fill-rule="evenodd"
											d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
											clip-rule="evenodd"
										></path>
									</svg>
								</div>
								<span class="text-green-800 font-semibold">Conversa processada com sucesso!</span>
							</div>
							<p class="text-green-700 text-sm mt-2">
								Selecione um novo arquivo para processar outra conversa.
							</p>
						</div>
					{/if}
				</form>
			</div>
		</div>

		<!-- NAO REMOVA ESSA INPUT, ELA É USADA PRA GERAR O PDF -->
		<input
			data-testid="playwright-inject-media"
			type="file"
			accept=".zip"
			on:change={handleBackendFileInjection}
			class="hidden"
		/>

		<!-- Chat renderizado - DESIGN WHATSAPP -->
		{#if messages?.length}
			<div
				class="chat-container relative bg-whatsapp-chat-bg rounded-3xl shadow-2xl border border-gray-300 mb-12 max-h-[75vh] overflow-hidden"
				data-testid="playwright-chat"
				bind:this={chatContainer}
			>
				<!-- Header do Chat -->
				<div
					class="sticky top-0 z-10 bg-gradient-to-r from-emerald-500/90 to-teal-500/90 backdrop-blur-xl p-6 border-b border-white/20"
				>
					<div class="flex items-center justify-between">
						<div class="flex items-center space-x-3">
							<div class="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
								<MessageCircle class="w-6 h-6 text-white" />
							</div>
							<div>
								<h3 class="text-lg font-semibold text-white">Conversa Organizada</h3>
								<p class="text-sm text-white/80">{messages.length} mensagens processadas</p>
							</div>
						</div>
						<div class="flex items-center space-x-2">
							<div class="px-3 py-1 bg-white/20 rounded-full">
								<span class="text-xs font-medium text-white">{isApple ? 'iOS' : 'Android'}</span>
							</div>
						</div>
					</div>
				</div>

				<!-- Container das mensagens -->
				<div
					class="message-container p-6 space-y-4 overflow-y-auto max-h-[calc(75vh-100px)] scroll-smooth bg-whatsapp-chat-pattern"
				>
					{#each messages as message, index}
						{@const attachedPdfMsg = message.FileAttached && message.links}
						{@const isOutgoing = getSideByDevice(isApple)[(message?.ID || 1) - 1] === 'right'}

						<div class="message-wrapper animate-slide-in" style="animation-delay: {index * 0.05}s">
							<div class="flex {isOutgoing ? 'justify-end' : 'justify-start'} mb-3">
								<div class="max-w-[75%] sm:max-w-[85%] group">
									<!-- Bubble da mensagem -->
									<div
										class="relative message-bubble {isOutgoing
											? 'bg-whatsapp-sent text-gray-800 message-sent'
											: 'bg-white text-gray-800 message-received'} 
										p-4 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1"
									>
										<!-- Header da mensagem -->
										<div class="flex justify-between items-center mb-2">
											<span
												class="text-sm font-semibold {isOutgoing
													? 'text-green-700'
													: 'text-blue-600'}"
											>
												{message.Name}
											</span>
											<span class="text-xs text-gray-500 ml-3">
												{message.Date}
											</span>
										</div>

										<!-- Conteúdo da mensagem -->
										<div class="message-content w-full min-w-0">
											{#if message.FileAttached}
												<!-- Anexos PDF -->
												{#if attachedPdfMsg}
													<div class="mb-2">
														<div
															class="flex items-center space-x-2 mb-2 p-2 {isOutgoing
																? 'bg-black/5'
																: 'bg-gray-50'} rounded-lg"
														>
															<FileText class="w-4 h-4 text-gray-600 flex-shrink-0" />
															<span class="text-sm text-gray-600 truncate">
																{getFileName(message.FileAttached)}
															</span>
														</div>
														<!-- Grid de imagens do PDF -->
														<div class="grid grid-cols-2 gap-2 mb-3">
															{#each message.links as link, linkIndex}
																{#if !(linkIndex % 2) && message.links[linkIndex + 1] !== 'pdf'}
																	<div
																		class="relative overflow-hidden rounded cursor-pointer"
																		on:click={() =>
																			openMediaModal(
																				link,
																				getFileName(message.FileAttached),
																				'pdf',
																				message.links
																			)}
																		on:keydown={(e) =>
																			e.key === 'Enter' &&
																			openMediaModal(
																				link,
																				getFileName(message.FileAttached),
																				'pdf',
																				message.links
																			)}
																		tabindex="0"
																		role="button"
																		aria-label="Visualizar PDF em tamanho maior"
																	>
																		<img
																			src={link}
																			alt="Página do Documento"
																			class="w-full h-24 object-cover"
																		/>
																		<div
																			class="absolute inset-0 bg-gradient-to-t from-black/30 to-transparent flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity"
																		>
																			<div class="bg-white/90 rounded-full p-2">
																				<FileText class="w-4 h-4 text-gray-700" />
																			</div>
																		</div>
																	</div>
																{/if}
															{/each}
														</div>
														<!-- Link para PDF completo -->
														{#if message.links && message.links.length >= 2 && message.links[1] === 'pdf'}
															<a
																href={message.links[0]}
																target="_blank"
																rel="noopener noreferrer"
																class="inline-flex items-center space-x-1 text-sm text-blue-600 hover:text-blue-700 underline underline-offset-2 hover:no-underline transition-colors"
															>
																<FileText class="w-3 h-3 flex-shrink-0" />
																<span class="truncate">Baixar PDF completo</span>
															</a>
														{/if}
													</div>
												{/if}

												<!-- Arquivos de áudio -->
												{#if isAudioFile(message.FileAttached)}
													<div class="mb-2 w-full max-w-full overflow-hidden">
														<div class="w-full max-w-full">
															<Audio
																filename={getFileName(message.FileAttached)}
																fileUrl={message.FileURL}
																audioTranscription={message.AudioTranscription}
															/>
														</div>
													</div>
													<!-- Imagens -->
												{:else if isImgFile(message.FileAttached)}
													<div class="mb-2" data-testid="imagem">
														<div
															class="relative overflow-hidden rounded-lg shadow-lg max-w-xs cursor-pointer transform hover:scale-105 transition-all duration-300"
															on:click={() =>
																openMediaModal(
																	message.FileURL,
																	getFileName(message.FileAttached),
																	'image'
																)}
															on:keydown={(e) =>
																e.key === 'Enter' &&
																openMediaModal(
																	message.FileURL,
																	getFileName(message.FileAttached),
																	'image'
																)}
															tabindex="0"
															role="button"
															aria-label="Visualizar imagem em tamanho maior"
														>
															<img
																src={message.FileURL}
																alt="Mídia compartilhada"
																class="w-full h-auto object-cover"
															/>
															<div
																class="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent opacity-0 hover:opacity-100 transition-opacity flex items-center justify-center"
															>
																<div class="bg-white/90 rounded-full p-3">
																	<div class="w-4 h-4 border-2 border-gray-700 rounded-sm"></div>
																</div>
															</div>
														</div>
													</div>
													<!-- Vídeos -->
												{:else if isVideoFile(message.FileAttached)}
													<div class="mb-2">
														<div class="rounded-lg overflow-hidden shadow-lg max-w-xs">
															<Video fileURL={message.FileURL} />
														</div>
													</div>
													<!-- Arquivos Word -->
												{:else if isWordFile(message.FileAttached)}
													<div
														class="flex items-center space-x-2 p-2 {isOutgoing
															? 'bg-black/5'
															: 'bg-gray-50'} rounded-lg"
													>
														<FileText class="w-4 h-4 text-gray-600 flex-shrink-0" />
														<span class="text-sm text-gray-600 truncate">
															{getFileName(message.FileAttached)}
														</span>
													</div>
												{/if}
											{:else}
												<!-- Mensagem de texto -->
												<div
													class="text-sm leading-relaxed whitespace-pre-wrap break-words"
													data-testid="texto"
												>
													{message.Message}
												</div>
											{/if}
										</div>

										<!-- Horário da mensagem (estilo WhatsApp) -->
										<div class="flex justify-end items-end mt-1 mb-0">
											<span class="text-xs text-gray-500 leading-none">
												{formatTime(message.Time)}
											</span>
											<!-- Indicador de lida apenas para mensagens enviadas -->
										{#if isOutgoing}
										<span class="text-xs text-gray-400"></span>
										{/if}										</div>

										<!-- Indicador de lida (apenas para mensagens enviadas) -->
										{#if isOutgoing}
											<div class="flex justify-end mt-2">
												<div class="flex space-x-1"></div>
											</div>
										{/if}
									</div>
								</div>
							</div>
						</div>
					{/each}
				</div>

				<!-- Footer do chat -->
				<div class="sticky bottom-0 bg-whatsapp-header p-3 border-t border-gray-200/50">
					<div class="flex justify-center">
						<div class="flex items-center space-x-2 text-xs text-gray-500">
							<div class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
							<span>Conversa processada e organizada</span>
						</div>
					</div>
				</div>
			</div>
		{/if}

		<!-- Instruções -->
		<div class="max-w-3xl mx-auto mb-12">
			<div class="bg-white/90 backdrop-blur-xl rounded-2xl shadow-xl border border-white/50 p-8">
				<h3 class="text-xl font-bold text-gray-800 mb-6">Como usar o WhatsOrganizer</h3>
				<p class="text-gray-600 leading-relaxed mb-6">
					Faça o upload do seu arquivo exportado do WhatsApp em formato <b>.zip</b>.
				</p>
				<div class="flex justify-center gap-6">
					<a
						href="https://faq.whatsapp.com/1180414079177245/?cms_platform=iphone&helpref=platform_switcher"
						class="bg-gray-200 p-4 rounded-full hover:bg-emerald-100 transition"
					>
						<img src="/apple.png" alt="Apple" class="w-8 h-8" />
					</a>
					<a
						href="https://faq.whatsapp.com/1180414079177245/?helpref=uf_share"
						class="bg-gray-200 p-4 rounded-full hover:bg-emerald-100 transition"
					>
						<img src="/android.png" alt="Android" class="w-8 h-8" />
					</a>
				</div>
			</div>
		</div>

		<!-- Botões extra -->
		<div class="text-center space-x-4">
			<button
				class="bg-white/20 backdrop-blur-md hover:bg-white/30 text-white font-semibold py-3 px-6 rounded-xl border border-white/30 transition-all duration-300 hover:scale-105"
				on:click={toggleLimitacoesModal}
				data-tetstid="limitacoes-btn"
			>
				Limitações
			</button>
			<button
				class="bg-white/20 backdrop-blur-md hover:bg-white/30 text-white font-semibold py-3 px-6 rounded-xl border border-white/30 transition-all duration-300 hover:scale-105"
				on:click={toggleLGPDModal}
				data-tetstid="lgpd-btn"
			>
				LGPD
			</button>
		</div>

		<!-- Floating PDF download -->
		{#if messages?.length}
			<!-- Comentado conforme original -->
		{/if}
	</div>

	<!-- Modal de Mídia -->
	{#if showMediaModal && currentMedia}
		<div
			role="button"
			tabindex="0"
			on:click={toggleMediaModal}
			on:keydown={(e) => e.key === 'Enter' && toggleMediaModal()}
			class="fixed inset-0 bg-black/80 backdrop-blur-sm flex justify-center items-center z-50 p-4"
			transition:fade={{ duration: 300 }}
>
			<div
				class="relative bg-white rounded-2xl shadow-2xl max-w-6xl max-h-[90vh] overflow-hidden"
				on:click|stopPropagation
				role="presentation"
				tabindex="-1"
				>
				<!-- Header do Modal -->
				<div class="flex items-center justify-between p-4 bg-whatsapp-header text-gray-800">
					<div class="flex items-center space-x-3 min-w-0 flex-1">
						<FileText class="w-5 h-5 flex-shrink-0" />
						<span class="font-semibold truncate">{currentMedia.filename}</span>
					</div>
					<div class="flex items-center space-x-2 flex-shrink-0">
						{#if currentMedia.type === 'pdf' && currentMedia.links && currentMedia.links.length >= 2 && currentMedia.links[1] === 'pdf'}
							<a
								href={currentMedia.links[0]}
								target="_blank"
								rel="noopener noreferrer"
								class="p-2 hover:bg-gray-100 rounded-lg transition-colors"
								title="Baixar PDF completo"
							>
								<Download class="w-5 h-5" />
							</a>
						{/if}
						<button
							on:click={toggleMediaModal}
							class="p-2 hover:bg-gray-100 rounded-lg transition-colors"
							title="Fechar"
						>
							<X class="w-5 h-5" />
						</button>
					</div>
				</div>

				<!-- Conteúdo do Modal -->
				<div class="p-6 overflow-auto max-h-[calc(90vh-80px)]">
					{#if currentMedia.type === 'image'}
						<!-- Imagem em tamanho grande -->
						<div class="flex justify-center">
							<img
								src={currentMedia.src}
								alt={currentMedia.filename}
								class="max-w-full max-h-[70vh] object-contain rounded-lg shadow-lg"
							/>
						</div>
					{:else if currentMedia.type === 'pdf'}
						<!-- PDF com todas as páginas -->
						<div class="space-y-6">
							<h3 class="text-lg font-semibold text-gray-800 mb-4">Visualização do Documento</h3>
							<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
								{#each currentMedia.links as link, linkIndex}
									{#if !(linkIndex % 2) && currentMedia.links[linkIndex + 1] !== 'pdf'}
										<div class="relative">
											<img
												src={link}
												alt="Página {Math.floor(linkIndex / 2) + 1}"
												class="w-full h-auto object-contain rounded-lg shadow-md border border-gray-200"
											/>
											<div
												class="absolute top-2 left-2 bg-black/70 text-white px-2 py-1 rounded text-xs"
											>
												Página {Math.floor(linkIndex / 2) + 1}
											</div>
										</div>
									{/if}
								{/each}
							</div>
						</div>
					{/if}
				</div>
			</div>
		</div>
	{/if}

	<!-- Modal de Limitações -->
	{#if showLimitacoesModal}
		<div
			class="fixed inset-0 bg-black/60 backdrop-blur-sm flex justify-center items-center z-50 p-4"
			on:click={toggleLimitacoesModal}
			data-testid="limitacoes-modal"
			role="presentation"
			tabindex="-1"
			transition:fade={{ duration: 300 }}
>
			<div
  class="bg-white rounded-2xl max-w-lg w-full shadow-2xl border border-gray-200 overflow-hidden transform transition-all duration-300 scale-95 hover:scale-100"
  on:click|stopPropagation
  role="presentation"
  tabindex="-1"
>
				<!-- Header do Modal -->
				<div class="bg-gradient-to-r from-orange-500 to-amber-500 px-8 py-6 text-white">
					<div class="flex items-center justify-between">
						<div class="flex items-center space-x-3">
							<div class="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center">
								<AlertTriangle class="w-6 h-6" />
							</div>
							<div>
								<h2 class="text-2xl font-bold tracking-tight">Limitações</h2>
								<p class="text-white/90 text-sm mt-1">Informações importantes sobre o sistema</p>
							</div>
						</div>
						<button
							on:click={toggleLimitacoesModal}
							class="p-2 hover:bg-white/20 rounded-lg transition-colors"
							title="Fechar"
						>
							<X class="w-5 h-5" />
						</button>
					</div>
				</div>

				<!-- Conteúdo -->
				<div class="px-8 py-8">
					<div class="space-y-6">
						<div class="flex items-start space-x-4">
							<div class="w-2 h-2 bg-orange-400 rounded-full mt-2 flex-shrink-0"></div>
							<div>
								<h4 class="font-semibold text-gray-900 mb-1">Grupos não suportados</h4>
								<p class="text-gray-600 text-sm leading-relaxed">
									Atualmente, o sistema processa apenas conversas individuais do WhatsApp.
								</p>
							</div>
						</div>

						<div class="flex items-start space-x-4">
							<div class="w-2 h-2 bg-orange-400 rounded-full mt-2 flex-shrink-0"></div>
							<div>
								<h4 class="font-semibold text-gray-900 mb-1">Limite de arquivo: {PUBLIC_MAX_UPLOAD_MB} MB</h4>
								<p class="text-gray-600 text-sm leading-relaxed">
									O tamanho máximo permitido para upload é de {PUBLIC_MAX_UPLOAD_MB} megabytes por arquivo.
								</p>
							</div>
						</div>

						<div class="flex items-start space-x-4">
							<div class="w-2 h-2 bg-orange-400 rounded-full mt-2 flex-shrink-0"></div>
							<div>
								<h4 class="font-semibold text-gray-900 mb-1">Sem garantia de autenticidade</h4>
								<p class="text-gray-600 text-sm leading-relaxed">
									O sistema não verifica a autenticidade das mensagens processadas.
								</p>
							</div>
						</div>
						<div class="flex items-start space-x-4">
							<div class="w-2 h-2 bg-orange-400 rounded-full mt-2 flex-shrink-0"></div>
							<div>
								<h4 class="font-semibold text-gray-900 mb-1">Projeto Open Source</h4>
								<p class="text-gray-600 text-sm leading-relaxed">
									Este sistema é <strong>open source</strong> e pode ser livremente auditado por
									qualquer pessoa. Confira o código completo no
									<a
										href="https://github.com/brpl20/whats-organizer-front"
										target="_blank"
										class="text-blue-600 hover:underline"
									>
										GitHub
									</a>.
								</p>
							</div>
						</div>
					</div>

					<div class="mt-8 pt-6 border-t border-gray-100">
						<div class="flex items-center space-x-2 text-amber-600">
							<Info class="w-4 h-4" />
							<span class="text-sm font-medium">
								Essas limitações ajudam a garantir o melhor desempenho do sistema.
							</span>
						</div>
					</div>
				</div>
			</div>
		</div>
	{/if}

	<!-- Modal de LGPD -->
	{#if showLGPDModal}
		<div
			class="fixed inset-0 bg-black/60 backdrop-blur-sm flex justify-center items-center z-50 p-4"
			on:click={toggleLGPDModal}
			data-testid="lgpd-modal"
			role="presentation"
			tabindex="-1"
			transition:fade={{ duration: 300 }}
>
		<div
				class="bg-white rounded-2xl max-w-lg w-full shadow-2xl border border-gray-200 overflow-hidden transform transition-all duration-300 scale-95 hover:scale-100"
				on:click|stopPropagation
				role="presentation"
				tabindex="-1"
>
				<!-- Header do Modal -->
				<div class="bg-gradient-to-r from-green-600 to-emerald-600 px-8 py-6 text-white">
					<div class="flex items-center justify-between">
						<div class="flex items-center space-x-3">
							<div class="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center">
								<Shield class="w-6 h-6" />
							</div>
							<div>
								<h2 class="text-2xl font-bold tracking-tight">LGPD</h2>
								<p class="text-white/90 text-sm mt-1">Lei Geral de Proteção de Dados</p>
							</div>
						</div>
						<button
							on:click={toggleLGPDModal}
							class="p-2 hover:bg-white/20 rounded-lg transition-colors"
							title="Fechar"
						>
							<X class="w-5 h-5" />
						</button>
					</div>
				</div>

				<!-- Conteúdo -->
				<div class="px-8 py-8">
					<div class="space-y-6">
						<div class="text-center">
							<div
								class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4"
							>
								<Shield class="w-8 h-8 text-green-600" />
							</div>
							<h3 class="text-xl font-bold text-gray-900 mb-2">Seus dados estão seguros</h3>
						</div>

						<div class="bg-green-50 rounded-xl p-6 border border-green-100">
							<p class="text-gray-700 leading-relaxed text-center">
								<strong class="text-green-800">Não coletamos nenhum dado pessoal</strong> e todos os
								arquivos enviados são automaticamente
								<strong class="text-green-800">destruídos após o processamento</strong>, garantindo
								total privacidade e segurança.
							</p>
						</div>

						<div class="grid grid-cols-2 gap-4 pt-4">
							<div class="text-center">
								<div
									class="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center mx-auto mb-2"
								>
									<span class="text-2xl">🚫</span>
								</div>
								<p class="text-sm font-semibold text-gray-700">Não coletamos</p>
								<p class="text-xs text-gray-500">dados pessoais</p>
							</div>
							<div class="text-center">
								<div
									class="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center mx-auto mb-2"
								>
									<span class="text-2xl">🗑️</span>
								</div>
								<p class="text-sm font-semibold text-gray-700">Arquivos removidos</p>
								<p class="text-xs text-gray-500">automaticamente</p>
							</div>
						</div>
					</div>

					<div class="mt-8 pt-6 border-t border-gray-100">
						<div class="flex items-center justify-center space-x-2 text-green-600">
							<Shield class="w-4 h-4" />
							<span class="text-sm font-medium"> 100% compatível com a LGPD </span>
						</div>
					</div>
				</div>
			</div>
		</div>
	{/if}
</main>

<style>
	/* Cores do WhatsApp exatas */
	:global(:root) {
		--whatsapp-bg: #0b141a;
		--whatsapp-chat-bg: #e5ddd5;
		--whatsapp-header: #ededed;
		--whatsapp-sent: #dcf8c6;
	}


	.bg-whatsapp-chat-bg {
		background: url('/whatsback.png') no-repeat center center;
		background-size: cover;
	}

	.bg-whatsapp-header {
		background-color: var(--whatsapp-header);
	}

	.bg-whatsapp-sent {
		background-color: var(--whatsapp-sent);
	}



	/* Padrão de fundo do WhatsApp exato */
	.bg-whatsapp-chat-pattern {
		background: url('/whatsback.png') no-repeat center center;
		background-size: cover;
	}

	/* Estilo dos balões de conversa WhatsApp */
	.message-bubble {
		border-radius: 12px;
		position: relative;
		max-width: 100%;
		word-wrap: break-word;
	}

	/* Triângulo do balão - mensagem enviada (direita) */
	.message-sent::after {
		content: '';
		position: absolute;
		bottom: 0;
		right: -6px;
		width: 0;
		height: 0;
		border-left: 12px solid var(--whatsapp-sent);
		border-bottom: 12px solid transparent;
		border-top: 0px solid transparent;
	}

	/* Triângulo do balão - mensagem recebida (esquerda) */
	.message-received::after {
		content: '';
		position: absolute;
		bottom: 0;
		left: -6px;
		width: 0;
		height: 0;
		border-right: 12px solid white;
		border-bottom: 12px solid transparent;
		border-top: 0px solid transparent;
	}

	@keyframes fade-in {
		from {
			opacity: 0;
			transform: translateY(20px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	@keyframes slide-in {
		from {
			opacity: 0;
			transform: translateX(-20px);
		}
		to {
			opacity: 1;
			transform: translateX(0);
		}
	}

	.animate-fade-in {
		animation: fade-in 0.8s ease-out;
	}

	.animate-slide-in {
		animation: slide-in 0.6s ease-out;
	}

	/* Scrollbar personalizado */
	.chat-container ::-webkit-scrollbar {
		width: 6px;
	}

	.chat-container ::-webkit-scrollbar-track {
		background: rgba(0, 0, 0, 0.05);
		border-radius: 10px;
	}

	.chat-container ::-webkit-scrollbar-thumb {
		background: linear-gradient(to bottom, #128c7e, #075e54);
		border-radius: 10px;
	}

	.chat-container ::-webkit-scrollbar-thumb:hover {
		background: linear-gradient(to bottom, #0f7a6b, #054f47);
	}

	/* Melhor responsividade para mensagens */
	@media (max-width: 768px) {
		.message-wrapper .max-w-\[75\%\] {
			max-width: 85%;
		}

		.message-content {
			overflow-wrap: break-word;
			word-break: break-word;
		}
	}

	/* Ajustes específicos para responsividade */
	@media (max-width: 640px) {
		.message-wrapper .max-w-\[75\%\] {
			max-width: 90%;
		}

		.message-wrapper .sm\:max-w-\[85\%\] {
			max-w: 95%;
		}
	}
</style>
