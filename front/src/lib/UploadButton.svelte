<script>
	import { createEventDispatcher } from 'svelte';
	import { fade } from 'svelte/transition';
	import UploadIcon from './UploadIcon.svelte';

	export let loading = false;

	/** @type {FileList} */
	let files = [];
	/** @type {HTMLInputElement | null} */
	let fileInput = null;
	let isDragging = false;

	let svgY = 45;
	$: files?.length && (svgY += files.length * 15);
	const dispatch = createEventDispatcher();
	$: dispatch('update', files);

	const handleDrop = (event) => {
		event.preventDefault();
		const droppedFiles = event.dataTransfer?.files;
		if (droppedFiles?.length > 0) {
			const dataTransfer = new DataTransfer();
			Array.from(droppedFiles).forEach((file) => dataTransfer.items.add(file));
			fileInput.files = dataTransfer.files;

			files = Array.from(droppedFiles);
		}
		isDragging = false;
	};

	const handleDragOver = (event) => {
		event.preventDefault();
		isDragging = true;
	};

	const handleDragLeave = () => {
		isDragging = false;
	};

	const triggerFileInput = () => {
		fileInput?.click();
	};

	const handleFileChange = (event) => {
		const selectedFiles = event.target.files;
		if (selectedFiles?.length > 0) {
			files = Array.from(selectedFiles);
		}
	};
</script>

<!-- Main Upload Card -->
<div class="max-w-2xl mx-auto mb-12">
	<div
		class="bg-white/95 backdrop-blur-xl rounded-3xl shadow-2xl border border-white/50 p-8 md:p-12"
	>
		<!-- Upload Area -->
		<button
			class={`w-full  rounded-2xl p-12 text-center transition-all duration-300 cursor-pointer group
        ${isDragging
				? "border-emerald-500 bg-emerald-50 scale-105"
				: "border-gray-300 bg-gray-50 hover:bg-gray-100 hover:border-gray-400"}`}
			on:dragover|preventDefault={handleDragOver}
			on:dragleave={handleDragLeave}
			on:drop|preventDefault={handleDrop}
			on:click={triggerFileInput}
			type="button"
			aria-label="Drop files here or click to upload"
		>
			<div class="flex flex-col items-center space-y-4">
				<!-- Ícone / Spinner -->
				<div
					class={`p-6 rounded-full transition-all duration-300
          ${isDragging
						? "bg-emerald-500 scale-110"
						: "bg-gray-200 group-hover:bg-emerald-100"}`}
				>
					{#if loading}
						<div class="spinner-container" transition:fade>
							<div
								class="spinner border-4 border-emerald-500 border-t-transparent rounded-full w-12 h-12 animate-spin"
								aria-label="Carregando"
							></div>
						</div>
					{:else}
						<UploadIcon
							class={`w-12 h-12 transition-colors duration-300
              ${isDragging
								? "text-white"
								: "text-gray-600 group-hover:text-emerald-600"}`}
						/>
					{/if}
				</div>

				<!-- Texto / Lista -->
				{#if files.length > 0}
					<div class="text-center">
						<p class="text-lg font-semibold text-emerald-600 mb-2">
							Arquivos selecionados:
						</p>
						<ul class="space-y-2">
							{#each files as file}
								<li
									class="text-gray-700 bg-emerald-50 px-4 py-2 rounded-lg inline-block text-sm"
								>
									{file.name}
								</li>
							{/each}
						</ul>
					</div>
				{:else}
					<div class="text-center">
						<p class="text-xl font-semibold text-gray-700 mb-2">
							Arraste seu arquivo aqui
						</p>
						<p class="text-gray-500 mb-4">ou clique para selecionar</p>
						<p class="text-sm text-gray-400">
							Suporta arquivos .zip exportados do WhatsApp
						</p>
					</div>
				{/if}
			</div>

			<!-- Input escondido -->
			<input
			class="hidden"
			type="file"
				bind:this={fileInput}
				accept=".zip"
				on:change={(e) => {
					console.log('lel')
					if (fileInput?.files) {
						files = Array.from(fileInput.files);
					}
				}}
			/>
		</button>

		<!-- Action Button -->
		<div class="mt-8 text-center">
			<button
			data-testid="submit-zip-btn"
		disabled={files.length === 0}
		class="bg-gradient-to-r from-emerald-600 to-teal-600 
		       hover:from-emerald-700 hover:to-teal-700 
		       text-white font-bold py-4 px-12 rounded-2xl shadow-lg 
		       transition-all duration-300 text-lg
		       disabled:opacity-50 disabled:cursor-not-allowed"
			   type="submit"
	>
			
				<div class="flex items-center space-x-3">
					<span>Processar Arquivo</span>
				</div>
			</button>
		</div>
	</div>
</div>

<style>
	.spinner-container {
		display: flex;
		justify-content: center;
		align-items: center;
	}
</style>