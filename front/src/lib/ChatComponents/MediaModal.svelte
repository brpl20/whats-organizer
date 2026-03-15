<script>
	import { fade } from 'svelte/transition';
	import { FileText, Download, X } from 'lucide-svelte';

	/**
	 * @type {{
	 *   media: import('../services/types').MediaModalData | null,
	 *   onClose: () => void
	 * }}
	 */
	let { media, onClose } = $props();
</script>

{#if media}
	<div
		role="button"
		tabindex="0"
		onclick={onClose}
		onkeydown={(e) => e.key === 'Enter' && onClose()}
		class="fixed inset-0 bg-black/80 backdrop-blur-sm flex justify-center items-center z-50 p-4"
		transition:fade={{ duration: 300 }}
	>
		<div
			class="relative bg-white rounded-2xl shadow-2xl max-w-6xl max-h-[90vh] overflow-hidden"
			onclick={(e) => e.stopPropagation()}
			onkeydown={() => {}}
			role="presentation"
			tabindex="-1"
		>
			<!-- Header -->
			<div class="flex items-center justify-between p-4 bg-whatsapp-header text-gray-800">
				<div class="flex items-center space-x-3 min-w-0 flex-1">
					<FileText class="w-5 h-5 flex-shrink-0" />
					<span class="font-semibold truncate">{media.filename}</span>
				</div>
				<div class="flex items-center space-x-2 flex-shrink-0">
					{#if media.type === 'pdf' && media.links?.length >= 2 && media.links[1] === 'pdf'}
						<a
							href={media.links[0]}
							target="_blank"
							rel="noopener noreferrer"
							class="p-2 hover:bg-gray-100 rounded-lg transition-colors"
							title="Baixar PDF completo"
						>
							<Download class="w-5 h-5" />
						</a>
					{/if}
					<button
						onclick={onClose}
						class="p-2 hover:bg-gray-100 rounded-lg transition-colors"
						title="Fechar"
					>
						<X class="w-5 h-5" />
					</button>
				</div>
			</div>

			<!-- Content -->
			<div class="p-6 overflow-auto max-h-[calc(90vh-80px)]">
				{#if media.type === 'image'}
					<div class="flex justify-center">
						<img
							src={media.src}
							alt={media.filename}
							class="max-w-full max-h-[70vh] object-contain rounded-lg shadow-lg"
						/>
					</div>
				{:else if media.type === 'pdf'}
					<div class="space-y-6">
						<h3 class="text-lg font-semibold text-gray-800 mb-4">
							Visualizacao do Documento
						</h3>
						<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
							{#each media.links as link, linkIndex}
								{#if !(linkIndex % 2) && media.links[linkIndex + 1] !== 'pdf'}
									<div class="relative">
										<img
											src={link}
											alt="Pagina {Math.floor(linkIndex / 2) + 1}"
											class="w-full h-auto object-contain rounded-lg shadow-md border border-gray-200"
										/>
										<div
											class="absolute top-2 left-2 bg-black/70 text-white px-2 py-1 rounded text-xs"
										>
											Pagina {Math.floor(linkIndex / 2) + 1}
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
