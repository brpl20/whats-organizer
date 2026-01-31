<script>
	export let data;
</script>

<svelte:head>
	<title>Blog - WhatsOrganizer</title>
	<meta name="description" content="Artigos sobre WhatsApp, privacidade, LGPD e dicas para organizar suas conversas." />
</svelte:head>

<main class="min-h-screen bg-gradient-to-br from-emerald-400 via-teal-500 to-blue-600">
	<div class="container mx-auto px-4 py-16 max-w-4xl">
		<!-- Header -->
		<div class="text-center mb-12">
			<a href="/" class="inline-block mb-6 text-white/80 hover:text-white transition-colors">
				&larr; Voltar ao WhatsOrganizer
			</a>
			<h1 class="text-4xl md:text-5xl font-bold text-white mb-4">Blog</h1>
			<p class="text-lg text-white/90">
				Dicas, tutoriais e novidades sobre o WhatsOrganizer
			</p>
		</div>

		<!-- Post listing -->
		<div class="space-y-6">
			{#each data.posts as post}
				<a
					href="/blog/{post.slug}"
					class="block bg-white/95 backdrop-blur-xl rounded-2xl shadow-xl border border-white/50 p-8 hover:shadow-2xl transition-all duration-300 hover:-translate-y-1"
				>
					<article>
						<time class="text-sm text-gray-500" datetime={post.date}>
							{new Date(post.date).toLocaleDateString('pt-BR', {
								year: 'numeric',
								month: 'long',
								day: 'numeric'
							})}
						</time>
						<h2 class="text-2xl font-bold text-gray-800 mt-2 mb-3">
							{post.title}
						</h2>
						<p class="text-gray-600 leading-relaxed">
							{post.description}
						</p>
						<span class="inline-block mt-4 text-emerald-600 font-semibold">
							Ler mais &rarr;
						</span>
					</article>
				</a>
			{/each}
		</div>

		{#if data.posts.length === 0}
			<div class="text-center text-white/80 py-12">
				<p>Nenhum artigo publicado ainda.</p>
			</div>
		{/if}
	</div>
</main>
