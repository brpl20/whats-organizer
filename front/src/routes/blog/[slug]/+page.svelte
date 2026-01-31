<script>
	export let data;
</script>

<svelte:head>
	<title>{data.post.meta.title} - WhatsOrganizer Blog</title>
	<meta name="description" content={data.post.meta.description} />
	<meta property="og:title" content={data.post.meta.title} />
	<meta property="og:description" content={data.post.meta.description} />
	<meta property="og:type" content="article" />
	<meta property="article:published_time" content={data.post.meta.date} />
	<meta property="article:author" content={data.post.meta.author} />
</svelte:head>

<main class="min-h-screen bg-gradient-to-br from-emerald-400 via-teal-500 to-blue-600">
	<div class="container mx-auto px-4 py-16 max-w-3xl">
		<!-- Navigation -->
		<div class="mb-8">
			<a href="/blog" class="text-white/80 hover:text-white transition-colors">
				&larr; Voltar ao Blog
			</a>
		</div>

		<!-- Article -->
		<article class="bg-white/95 backdrop-blur-xl rounded-2xl shadow-xl border border-white/50 p-8 md:p-12">
			<header class="mb-8 border-b border-gray-200 pb-6">
				<time class="text-sm text-gray-500" datetime={data.post.meta.date}>
					{new Date(data.post.meta.date).toLocaleDateString('pt-BR', {
						year: 'numeric',
						month: 'long',
						day: 'numeric'
					})}
				</time>
				<h1 class="text-3xl md:text-4xl font-bold text-gray-800 mt-2">
					{data.post.meta.title}
				</h1>
				{#if data.post.meta.author}
					<p class="text-gray-500 mt-2">Por {data.post.meta.author}</p>
				{/if}
			</header>

			<div class="prose prose-lg max-w-none">
				{@html data.post.html}
			</div>
		</article>

		<!-- Back to home -->
		<div class="text-center mt-8">
			<a
				href="/"
				class="inline-block bg-white/20 backdrop-blur-md hover:bg-white/30 text-white font-semibold py-3 px-6 rounded-xl border border-white/30 transition-all duration-300"
			>
				Voltar ao WhatsOrganizer
			</a>
		</div>
	</div>
</main>

<style>
	.prose h1 { font-size: 2em; font-weight: 700; margin-top: 1.5em; margin-bottom: 0.5em; color: #1f2937; }
	.prose h2 { font-size: 1.5em; font-weight: 600; margin-top: 1.5em; margin-bottom: 0.5em; color: #1f2937; }
	.prose h3 { font-size: 1.25em; font-weight: 600; margin-top: 1.25em; margin-bottom: 0.5em; color: #1f2937; }
	.prose p { margin-top: 1em; margin-bottom: 1em; color: #374151; line-height: 1.75; }
	.prose ul { list-style-type: disc; padding-left: 1.5em; margin-top: 0.5em; margin-bottom: 0.5em; }
	.prose ol { list-style-type: decimal; padding-left: 1.5em; margin-top: 0.5em; margin-bottom: 0.5em; }
	.prose li { margin-top: 0.25em; margin-bottom: 0.25em; color: #374151; }
	.prose strong { font-weight: 700; }
	.prose a { color: #059669; text-decoration: underline; }
	.prose a:hover { color: #047857; }
	.prose code { background-color: #f3f4f6; padding: 0.2em 0.4em; border-radius: 0.25rem; font-size: 0.875em; }
	.prose pre { background-color: #1f2937; color: #e5e7eb; padding: 1em; border-radius: 0.5rem; overflow-x: auto; margin-top: 1em; margin-bottom: 1em; }
	.prose blockquote { border-left: 4px solid #d1d5db; padding-left: 1em; margin-left: 0; color: #6b7280; font-style: italic; }
</style>
