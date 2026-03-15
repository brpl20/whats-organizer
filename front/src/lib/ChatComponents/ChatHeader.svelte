<script>
	import { MessageCircle } from 'lucide-svelte';

	/** @type {{ messageCount: number, isApple: boolean }} */
	let { messageCount, isApple } = $props();
</script>

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
				<p class="text-sm text-white/80">
					{messageCount} mensagens processadas
				</p>
			</div>
		</div>
		<div class="flex items-center space-x-2">
			<div class="px-3 py-1 bg-white/20 rounded-full">
				<span class="text-xs font-medium text-white">{isApple ? 'iOS' : 'Android'}</span>
			</div>
		</div>
	</div>
</div>
