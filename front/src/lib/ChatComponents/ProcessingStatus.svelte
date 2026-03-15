<script>
	/** @type {{ isProcessing: boolean, isComplete: boolean }} */
	let { isProcessing, isComplete } = $props();
</script>

{#if isProcessing}
	<div class="bg-blue-100 border border-blue-300 rounded-xl p-4 text-center">
		<div class="flex items-center justify-center space-x-2">
			<div
				class="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"
			></div>
			<span class="text-blue-800 font-semibold">Processando conversa...</span>
		</div>
		<p class="text-blue-700 text-sm mt-2">Aguarde enquanto processamos seu arquivo.</p>
	</div>
{:else if isComplete}
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
