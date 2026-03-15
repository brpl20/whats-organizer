<script>
	import { FileText } from 'lucide-svelte';
	import Audio from './Audio.svelte';
	import Video from './Video.svelte';
	import {
		isAudioFile,
		isVideoFile,
		isImgFile,
		isWordFile,
		getFileName,
		formatTime
	} from '../services/file-utils.js';

	/**
	 * @type {{
	 *   message: import('../services/types').Message,
	 *   isOutgoing: boolean,
	 *   index: number,
	 *   onMediaClick: (src: string, filename: string, type: string, links?: string[]) => void
	 * }}
	 */
	let { message, isOutgoing, index, onMediaClick } = $props();

	const attachedPdfMsg = $derived(message.FileAttached && message.links);
</script>

<div class="message-wrapper animate-slide-in" style="animation-delay: {index * 0.05}s">
	<div class="flex {isOutgoing ? 'justify-end' : 'justify-start'} mb-3">
		<div class="max-w-[75%] sm:max-w-[85%] group">
			<div
				class="relative message-bubble {isOutgoing
					? 'bg-whatsapp-sent text-gray-800 message-sent'
					: 'bg-white text-gray-800 message-received'}
				p-4 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1"
			>
				<!-- Header -->
				<div class="flex justify-between items-center mb-2">
					<span
						class="text-sm font-semibold {isOutgoing ? 'text-green-700' : 'text-blue-600'}"
					>
						{message.Name}
					</span>
					<span class="text-xs text-gray-500 ml-3">{message.Date}</span>
				</div>

				<!-- Content -->
				<div class="message-content w-full min-w-0">
					{#if message.FileAttached}
						<!-- PDF attachments -->
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
								<div class="grid grid-cols-2 gap-2 mb-3">
									{#each message.links as link, linkIndex}
										{#if !(linkIndex % 2) && message.links[linkIndex + 1] !== 'pdf'}
											<div
												class="relative overflow-hidden rounded cursor-pointer"
												onclick={() =>
													onMediaClick(
														link,
														getFileName(message.FileAttached),
														'pdf',
														message.links
													)}
												onkeydown={(e) =>
													e.key === 'Enter' &&
													onMediaClick(
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
													alt="Pagina do Documento"
													class="w-full h-24 object-cover"
													data-testid="pdf-page"
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
								{#if message.links?.length >= 2 && message.links[1] === 'pdf'}
									<a
										href={message.links[0]}
										target="_blank"
										rel="noopener noreferrer"
										class="inline-flex items-center space-x-1 text-sm text-blue-600 hover:text-blue-700 underline underline-offset-2 hover:no-underline transition-colors"
										data-testid="pdf-link"
									>
										<FileText class="w-3 h-3 flex-shrink-0" />
										<span class="truncate">Baixar PDF completo</span>
									</a>
								{/if}
							</div>
						{/if}

						<!-- Audio files -->
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
						{:else if isImgFile(message.FileAttached)}
							<div class="mb-2" data-testid="imagem">
								<div
									class="relative overflow-hidden rounded-lg shadow-lg max-w-xs cursor-pointer transform hover:scale-105 transition-all duration-300"
									onclick={() =>
										onMediaClick(
											message.FileURL,
											getFileName(message.FileAttached),
											'image'
										)}
									onkeydown={(e) =>
										e.key === 'Enter' &&
										onMediaClick(
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
										alt="Midia compartilhada"
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
						{:else if isVideoFile(message.FileAttached)}
							<div class="mb-2">
								<div class="rounded-lg overflow-hidden shadow-lg max-w-xs">
									<Video fileURL={message.FileURL} />
								</div>
							</div>
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
						<div
							class="text-sm leading-relaxed whitespace-pre-wrap break-words"
							data-testid="texto"
						>
							{message.Message}
						</div>
					{/if}
				</div>

				<!-- Timestamp -->
				<div class="flex justify-end items-end mt-1 mb-0">
					<span class="text-xs text-gray-500 leading-none">
						{formatTime(message.Time)}
					</span>
					{#if isOutgoing}
						<span class="text-xs text-gray-400"></span>
					{/if}
				</div>

				{#if isOutgoing}
					<div class="flex justify-end mt-2">
						<div class="flex space-x-1"></div>
					</div>
				{/if}
			</div>
		</div>
	</div>
</div>

<style>
	.message-bubble {
		border-radius: 12px;
		position: relative;
		max-width: 100%;
		word-wrap: break-word;
	}

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

	.animate-slide-in {
		animation: slide-in 0.6s ease-out;
	}

	@media (max-width: 768px) {
		.message-wrapper :global(.max-w-\[75\%\]) {
			max-width: 85%;
		}
		.message-content {
			overflow-wrap: break-word;
			word-break: break-word;
		}
	}

	@media (max-width: 640px) {
		.message-wrapper :global(.max-w-\[75\%\]) {
			max-width: 90%;
		}
	}
</style>
