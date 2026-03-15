<script>
	import ChatHeader from './ChatHeader.svelte';
	import ChatMessage from './ChatMessage.svelte';
	import { getSideByDevice } from '../services/file-utils.js';

	/**
	 * @type {{
	 *   messages: import('../services/types').Message[],
	 *   isApple: boolean,
	 *   onMediaClick: (src: string, filename: string, type: string, links?: string[]) => void
	 * }}
	 */
	let { messages, isApple, onMediaClick } = $props();

	/** @type {HTMLDivElement | undefined} */
	let chatContainer = $state(undefined);
</script>

<div
	class="chat-container relative bg-whatsapp-chat-bg rounded-3xl shadow-2xl border border-gray-300 mb-12 max-h-[75vh] overflow-hidden"
	data-testid="playwright-chat"
	bind:this={chatContainer}
>
	<ChatHeader messageCount={messages.length} {isApple} />

	<div
		class="message-container p-6 space-y-4 overflow-y-auto max-h-[calc(75vh-100px)] scroll-smooth bg-whatsapp-chat-pattern"
	>
		{#each messages as message, index}
			{@const isOutgoing =
				getSideByDevice(isApple)[(message?.ID || 1) - 1] === 'right'}
			<ChatMessage {message} {isOutgoing} {index} {onMediaClick} />
		{/each}
	</div>

	<!-- Footer -->
	<div class="sticky bottom-0 bg-whatsapp-header p-3 border-t border-gray-200/50">
		<div class="flex justify-center">
			<div class="flex items-center space-x-2 text-xs text-gray-500">
				<div class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
				<span>Conversa processada e organizada</span>
			</div>
		</div>
	</div>
</div>

<style>
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

	:global(.bg-whatsapp-header) {
		background-color: var(--whatsapp-header);
	}

	:global(.bg-whatsapp-sent) {
		background-color: var(--whatsapp-sent);
	}

	.bg-whatsapp-chat-pattern {
		background: url('/whatsback.png') no-repeat center center;
		background-size: cover;
	}

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
</style>
