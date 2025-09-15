<script>
	import { onDestroy } from 'svelte';
	import CloseSvg from './CloseSvg.svelte';

	/**
	 * @typedef {import('./types/toast.type.js').ToastProps} ToastProps
	 */

	/** @type {ToastProps['svg']} */
	export let svg = null;

	/** @type {ToastProps['text']} */
	export let text = '';

	/** @type {ToastProps['onClose']} */
	export let onClose = () => undefined;

	/** @type {ToastProps['closed']} */
	export let closed = false;

	/** @type {ToastProps['error']} */
	export let error = false;

	let internallyDismissed = false;
	let removed = false;

	$: if (removed) onClose?.();

	const clearInternalTimeout = () => typeof timeout === 'number' && clearTimeout(timeout);

	const requestAnimatedDismiss = () => {
		internallyDismissed = true;
		clearInternalTimeout();
		timeout = setTimeout(() => (removed = true), 300);
	};

	const requestAnimatedPopup = () => {
		if (!text) return;
		removed = false;
		internallyDismissed = true;
		clearInternalTimeout();
		timeout = setTimeout(() => (internallyDismissed = false), 300);
	}; 

	let prevText = '';
	const showNewToast = () => {
		const previouslyInternallyDismissed = removed && !closed;
		if (!previouslyInternallyDismissed) return;
		requestAnimatedPopup();
	}

	$: if (prevText !== text) {
		prevText = text;
		showNewToast();
	}

	$: if (closed) requestAnimatedDismiss();
	$: if (!closed) requestAnimatedPopup();

	onDestroy(clearInternalTimeout);

	/** @type {NodeJS.Timeout} */
	let timeout = null;

	const onDismiss = () => {
		requestAnimatedDismiss();
	};

</script>

{#if !removed}
	<div class="fixed z-50 left-1/2 -translate-x-1/2 mt-4" data-testid={`toast${error ? '-error' : '-info'}`}>
		<div
			role="alert"
			class="
				flex items-center w-72 min-h-[4rem] px-4 py-2 rounded-2xl shadow-lg border
				transition-opacity duration-300 ease-in-out
				{closed || internallyDismissed ? 'opacity-0' : 'opacity-100'}
				{error 
					? 'from-red-50 to-red-100 border-red-300 text-red-800' 
					: 'from-green-50 to-green-100 border-green-300 text-green-800'}
			"
		>
			<div
				class="
					inline-flex items-center justify-center flex-shrink-0 w-8 h-8 rounded-lg
					{error 
						? 'bg-red-200 text-red-700' 
						: 'bg-green-200 text-green-700'}
				"
			>
				<svelte:component this={svg} class="w-4 h-4" />
				<span class="sr-only">{error ? 'Erro' : 'Notificação'}</span>
			</div>

			<div class="ml-4 text-sm font-medium flex-1">
				{error ? (text || "Erro Desconhecido!") : (text || "")}
			</div>

			<button 
				type="button" 
				class="ml-auto -mr-1.5 rounded-lg p-1.5 bg-white/60 text-gray-500 hover:bg-gray-50 hover:text-gray-700 transition-colors duration-200"
				on:click={onDismiss}
				aria-label="Close"
			>
				<span class="sr-only">Close</span>
				<CloseSvg class="w-4 h-4" />
			</button>
		</div>
	</div>
{/if}

<style>
	/* Estilos base do TailwindCSS já estão aplicados nas classes do HTML. */
	/* Adicione aqui quaisquer estilos customizados que o Tailwind não cubra diretamente. */

	/* Exemplo: Se precisar de um gradiente mais específico ou transição customizada */
	.from-green-50 { background-image: linear-gradient(to right, var(--tw-gradient-stops, #ecfeff, #a7f3d0)); }
	.to-green-100 { background-image: linear-gradient(to right, var(--tw-gradient-stops, #ecfeff, #a7f3d0)); }
	.from-red-50 { background-image: linear-gradient(to right, var(--tw-gradient-stops, #fff1f2, #fed7d7)); }
	.to-red-100 { background-image: linear-gradient(to right, var(--tw-gradient-stops, #fff1f2, #fed7d7)); }

	.border-green-300 { border-color: #6ee7b7; }
	.border-red-300 { border-color: #f97316; }
	.text-green-800 { color: #145a32; }
	.text-red-800 { color: #742a2a; }

	.bg-green-200 { background-color: #86efac; }
	.text-green-700 { color: #166534; }
	.bg-red-200 { background-color: #fca5a3; }
	.text-red-700 { color: #991b1b; }

	.shadow-lg { box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05); }

	/* Customização para os botões */
	.hover\:bg-gray-50:hover { background-color: #f9fafb; }
	.hover\:text-gray-700:hover { color: #374151; }

	/* Classe para o ícone do close SVG, caso você não esteja passando a classe diretamente */
	.w-4 { width: 1rem; }
	.h-4 { height: 1rem; }
	.sr-only {
		position: absolute;
		width: 1px;
		height: 1px;
		padding: 0;
		margin: -1px;
		overflow: hidden;
		clip: rect(0, 0, 0, 0);
		white-space: nowrap;
		border-width: 0;
	}
</style>
