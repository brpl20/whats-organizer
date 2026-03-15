<script>
	import { fade } from 'svelte/transition';
	import { MessageCircle, FileText, Upload } from 'lucide-svelte';
	import ChatView from '$lib/ChatComponents/ChatView.svelte';
	import MediaModal from '$lib/ChatComponents/MediaModal.svelte';
	import ProcessingStatus from '$lib/ChatComponents/ProcessingStatus.svelte';
	import PdfButton from '$lib/ChatComponents/PdfButton.svelte';
	import InfoModals from '$lib/ChatComponents/InfoModals.svelte';

	/** @type {import('$lib/services/types').Message[] | null} */
	let messages = $state(null);

	/** @type {import('$lib/services/types').MediaModalData | null} */
	let currentMedia = $state(null);

	let isApple = $state(false);
	let jsonText = $state('');
	let errorMsg = $state('');
	let showMediaModal = $state(false);

	/** @type {HTMLInputElement | null} */
	let fileInput = $state(null);

	function loadJson() {
		errorMsg = '';
		try {
			const parsed = JSON.parse(jsonText);

			// Support both raw array and {messages: [...]} format (from cli_test.py)
			const msgArray = Array.isArray(parsed) ? parsed : parsed.messages;

			if (!Array.isArray(msgArray) || msgArray.length === 0) {
				errorMsg = 'JSON deve ser um array de mensagens ou ter a chave "messages".';
				return;
			}

			messages = msgArray;
			isApple = messages[0]?.IsApple ?? false;
		} catch (e) {
			errorMsg = `JSON invalido: ${e.message}`;
		}
	}

	/** @param {Event & {currentTarget: HTMLInputElement}} e */
	function handleFileUpload(e) {
		const file = e.currentTarget.files?.[0];
		if (!file) return;

		const reader = new FileReader();
		reader.onload = () => {
			jsonText = /** @type {string} */ (reader.result);
			loadJson();
		};
		reader.readAsText(file);
	}

	function clear() {
		messages = null;
		jsonText = '';
		errorMsg = '';
		currentMedia = null;
		showMediaModal = false;
	}

	/**
	 * @param {string} src
	 * @param {string} filename
	 * @param {string} type
	 * @param {string[]} [links]
	 */
	function openMedia(src, filename, type, links = undefined) {
		currentMedia = { src, filename, type, links };
		showMediaModal = true;
	}

	function closeMedia() {
		showMediaModal = false;
		currentMedia = null;
	}
</script>

<main
	class="min-h-screen bg-gradient-to-br from-emerald-400 via-teal-500 to-blue-600 relative overflow-hidden"
>
	<div class="absolute inset-0 bg-black/5"></div>
	<div class="absolute top-20 left-10 w-72 h-72 bg-white/10 rounded-full blur-3xl"></div>
	<div class="absolute bottom-20 right-10 w-96 h-96 bg-emerald-300/20 rounded-full blur-3xl"></div>

	<div class="relative z-10 container mx-auto px-4 py-12">
		<!-- Header -->
		<div class="text-center mb-12 animate-fade-in">
			<div class="flex justify-center items-center mb-6">
				<div
					class="bg-white/20 backdrop-blur-md rounded-2xl p-4 shadow-2xl border border-white/30"
				>
					<MessageCircle class="w-12 h-12 text-white" />
				</div>
			</div>
			<h1 class="text-5xl md:text-6xl font-bold text-white mb-4 tracking-tight">
				WhatsOrganizer
			</h1>
			<p class="text-lg text-white/80">Teste de componentes — carregue um JSON do backend</p>
		</div>

		<!-- JSON Input Card -->
		<div class="max-w-3xl mx-auto mb-12">
			<div class="bg-white/95 backdrop-blur-xl rounded-3xl shadow-2xl border border-white/50 p-8">
				<div class="flex items-center justify-between mb-4">
					<h2 class="text-xl font-bold text-gray-800">Carregar JSON</h2>
					<div class="flex items-center space-x-2">
						<!-- File upload button -->
						<button
							onclick={() => fileInput?.click()}
							class="flex items-center space-x-2 bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium py-2 px-4 rounded-xl transition-colors text-sm"
						>
							<Upload class="w-4 h-4" />
							<span>Arquivo .json</span>
						</button>
						<input
							bind:this={fileInput}
							type="file"
							accept=".json"
							onchange={handleFileUpload}
							class="hidden"
						/>
					</div>
				</div>

				<p class="text-gray-500 text-sm mb-4">
					Cole o JSON gerado pelo <code class="bg-gray-100 px-1.5 py-0.5 rounded">cli_test.py</code>
					ou carregue um arquivo .json
				</p>

				<textarea
					bind:value={jsonText}
					placeholder={`{"messages": [{"Name": "Bruno", "ID": 1, ...}]}`}
					class="w-full h-48 p-4 border border-gray-300 rounded-xl font-mono text-sm resize-y focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all"
				></textarea>

				{#if errorMsg}
					<div
						class="mt-3 p-3 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm"
						transition:fade
					>
						{errorMsg}
					</div>
				{/if}

				<div class="flex justify-center space-x-4 mt-6">
					<button
						onclick={loadJson}
						disabled={!jsonText.trim()}
						class="bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white font-bold py-3 px-8 rounded-2xl shadow-lg transition-all duration-300 text-lg disabled:opacity-50 disabled:cursor-not-allowed"
					>
						Visualizar Chat
					</button>
					{#if messages?.length}
						<button
							onclick={clear}
							class="bg-gray-200 hover:bg-gray-300 text-gray-700 font-semibold py-3 px-8 rounded-2xl transition-all duration-300"
						>
							Limpar
						</button>
					{/if}
				</div>
			</div>
		</div>

		<!-- Processing Status (not used here, but shows component works) -->
		{#if messages === null && jsonText.trim()}
			<ProcessingStatus isProcessing={false} isComplete={false} />
		{/if}

		<!-- Chat View -->
		{#if messages?.length}
			<div class="max-w-4xl mx-auto" transition:fade={{ duration: 300 }}>
				<!-- Stats bar -->
				<div class="bg-white/90 backdrop-blur-xl rounded-2xl shadow-lg p-4 mb-6">
					<div class="flex justify-between items-center text-sm">
						<span class="text-gray-600">
							<strong>{messages.length}</strong> mensagens
						</span>
						<span class="text-gray-600">
							Dispositivo: <strong>{isApple ? 'iPhone' : 'Android'}</strong>
						</span>
						<span class="text-gray-600">
							Participantes:
							<strong>
								{[...new Set(messages.map((m) => m.Name))].join(', ')}
							</strong>
						</span>
					</div>
				</div>

				<ChatView {messages} {isApple} onMediaClick={openMedia} />
			</div>
		{/if}

		<!-- Info Modals -->
		<div class="mt-12">
			<InfoModals />
		</div>
	</div>

	<!-- Media Modal -->
	{#if showMediaModal}
		<MediaModal media={currentMedia} onClose={closeMedia} />
	{/if}
</main>

<style>
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

	.animate-fade-in {
		animation: fade-in 0.8s ease-out;
	}
</style>
