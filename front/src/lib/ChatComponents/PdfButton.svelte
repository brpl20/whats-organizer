<script>
	import { Download } from 'lucide-svelte';

	/** @type {{ isGenerating: boolean, onclick: () => void }} */
	let { isGenerating, onclick } = $props();
</script>

<button
	{onclick}
	disabled={isGenerating}
	class="fixed bottom-8 right-8 z-40 flex items-center space-x-2 bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-600 hover:to-teal-600 text-white font-semibold py-3 px-6 rounded-full shadow-2xl border border-white/20 transition-all duration-300 hover:scale-105 disabled:opacity-70 disabled:cursor-not-allowed disabled:hover:scale-100"
>
	{#if isGenerating}
		<div
			class="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"
		></div>
		<span>Gerando PDF...</span>
	{:else}
		<Download class="w-5 h-5" />
		<span>Download PDF</span>
	{/if}
</button>
