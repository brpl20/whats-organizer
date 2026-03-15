<script>
	import { fade } from 'svelte/transition';
	import { AlertTriangle, Shield, Info, X } from 'lucide-svelte';

	/** @type {{ maxUploadMb?: string }} */
	let { maxUploadMb = '100' } = $props();

	let showLimitacoes = $state(false);
	let showLGPD = $state(false);

	export const toggleLimitacoes = () => (showLimitacoes = !showLimitacoes);
	export const toggleLGPD = () => (showLGPD = !showLGPD);
</script>

<!-- Botoes -->
<div class="text-center space-x-4">
	<button
		class="bg-white/20 backdrop-blur-md hover:bg-white/30 text-white font-semibold py-3 px-6 rounded-xl border border-white/30 transition-all duration-300 hover:scale-105"
		onclick={() => (showLimitacoes = true)}
		data-testid="limitacoes-btn"
	>
		Limitacoes
	</button>
	<button
		class="bg-white/20 backdrop-blur-md hover:bg-white/30 text-white font-semibold py-3 px-6 rounded-xl border border-white/30 transition-all duration-300 hover:scale-105"
		onclick={() => (showLGPD = true)}
		data-testid="lgpd-btn"
	>
		LGPD
	</button>
</div>

<!-- Modal de Limitacoes -->
{#if showLimitacoes}
	<div
		class="fixed inset-0 bg-black/60 backdrop-blur-sm flex justify-center items-center z-50 p-4"
		onclick={() => (showLimitacoes = false)}
		data-testid="limitacoes-modal"
		role="presentation"
		tabindex="-1"
		transition:fade={{ duration: 300 }}
	>
		<div
			class="bg-white rounded-2xl max-w-lg w-full shadow-2xl border border-gray-200 overflow-hidden"
			onclick={(e) => e.stopPropagation()}
			role="presentation"
			tabindex="-1"
		>
			<div class="bg-gradient-to-r from-orange-500 to-amber-500 px-8 py-6 text-white">
				<div class="flex items-center justify-between">
					<div class="flex items-center space-x-3">
						<div
							class="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center"
						>
							<AlertTriangle class="w-6 h-6" />
						</div>
						<div>
							<h2 class="text-2xl font-bold tracking-tight">Limitacoes</h2>
							<p class="text-white/90 text-sm mt-1">
								Informacoes importantes sobre o sistema
							</p>
						</div>
					</div>
					<button
						onclick={() => (showLimitacoes = false)}
						class="p-2 hover:bg-white/20 rounded-lg transition-colors"
						title="Fechar"
					>
						<X class="w-5 h-5" />
					</button>
				</div>
			</div>

			<div class="px-8 py-8">
				<div class="space-y-6">
					<div class="flex items-start space-x-4">
						<div class="w-2 h-2 bg-orange-400 rounded-full mt-2 flex-shrink-0"></div>
						<div>
							<h4 class="font-semibold text-gray-900 mb-1">Grupos nao suportados*</h4>
							<p class="text-gray-600 text-sm leading-relaxed">
								Atualmente, o sistema processa apenas conversas individuais do WhatsApp.
							</p>
						</div>
					</div>
					<div class="flex items-start space-x-4">
						<div class="w-2 h-2 bg-orange-400 rounded-full mt-2 flex-shrink-0"></div>
						<div>
							<h4 class="font-semibold text-gray-900 mb-1">
								Limite de arquivo: {maxUploadMb} MB
							</h4>
							<p class="text-gray-600 text-sm leading-relaxed">
								O tamanho maximo permitido para upload e de {maxUploadMb} megabytes por
								arquivo.
							</p>
						</div>
					</div>
					<div class="flex items-start space-x-4">
						<div class="w-2 h-2 bg-orange-400 rounded-full mt-2 flex-shrink-0"></div>
						<div>
							<h4 class="font-semibold text-gray-900 mb-1">
								Sem garantia de autenticidade
							</h4>
							<p class="text-gray-600 text-sm leading-relaxed">
								O sistema nao verifica a autenticidade das mensagens processadas.
							</p>
						</div>
					</div>
					<div class="flex items-start space-x-4">
						<div class="w-2 h-2 bg-orange-400 rounded-full mt-2 flex-shrink-0"></div>
						<div>
							<h4 class="font-semibold text-gray-900 mb-1">Projeto Open Source</h4>
							<p class="text-gray-600 text-sm leading-relaxed">
								Este sistema e <strong>open source</strong> e pode ser livremente
								auditado por qualquer pessoa. Confira o codigo completo no
								<a
									href="https://github.com/brpl20/whats-organizer"
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
							Essas limitacoes ajudam a garantir o melhor desempenho do sistema.
						</span>
					</div>
				</div>
			</div>
		</div>
	</div>
{/if}

<!-- Modal de LGPD -->
{#if showLGPD}
	<div
		class="fixed inset-0 bg-black/60 backdrop-blur-sm flex justify-center items-center z-50 p-4"
		onclick={() => (showLGPD = false)}
		data-testid="lgpd-modal"
		role="presentation"
		tabindex="-1"
		transition:fade={{ duration: 300 }}
	>
		<div
			class="bg-white rounded-2xl max-w-lg w-full shadow-2xl border border-gray-200 overflow-hidden"
			onclick={(e) => e.stopPropagation()}
			role="presentation"
			tabindex="-1"
		>
			<div class="bg-gradient-to-r from-green-600 to-emerald-600 px-8 py-6 text-white">
				<div class="flex items-center justify-between">
					<div class="flex items-center space-x-3">
						<div
							class="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center"
						>
							<Shield class="w-6 h-6" />
						</div>
						<div>
							<h2 class="text-2xl font-bold tracking-tight">LGPD</h2>
							<p class="text-white/90 text-sm mt-1">Lei Geral de Protecao de Dados</p>
						</div>
					</div>
					<button
						onclick={() => (showLGPD = false)}
						class="p-2 hover:bg-white/20 rounded-lg transition-colors"
						title="Fechar"
					>
						<X class="w-5 h-5" />
					</button>
				</div>
			</div>

			<div class="px-8 py-8">
				<div class="space-y-6">
					<div class="text-center">
						<div
							class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4"
						>
							<Shield class="w-8 h-8 text-green-600" />
						</div>
						<h3 class="text-xl font-bold text-gray-900 mb-2">
							Seus dados estao seguros
						</h3>
					</div>
					<div class="bg-green-50 rounded-xl p-6 border border-green-100">
						<p class="text-gray-700 leading-relaxed text-center">
							<strong class="text-green-800">Nao coletamos nenhum dado pessoal</strong>
							e todos os arquivos enviados sao automaticamente
							<strong class="text-green-800">destruidos apos o processamento</strong>,
							garantindo total privacidade e seguranca.
						</p>
					</div>
					<div class="grid grid-cols-2 gap-4 pt-4">
						<div class="text-center">
							<div
								class="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center mx-auto mb-2"
							>
								<span class="text-2xl">&#128683;</span>
							</div>
							<p class="text-sm font-semibold text-gray-700">Nao coletamos</p>
							<p class="text-xs text-gray-500">dados pessoais</p>
						</div>
						<div class="text-center">
							<div
								class="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center mx-auto mb-2"
							>
								<span class="text-2xl">&#128465;</span>
							</div>
							<p class="text-sm font-semibold text-gray-700">Arquivos removidos</p>
							<p class="text-xs text-gray-500">automaticamente</p>
						</div>
					</div>
				</div>
				<div class="mt-8 pt-6 border-t border-gray-100">
					<div class="flex items-center justify-center space-x-2 text-green-600">
						<Shield class="w-4 h-4" />
						<span class="text-sm font-medium"> 100% compativel com a LGPD </span>
					</div>
				</div>
			</div>
		</div>
	</div>
{/if}
