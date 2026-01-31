import { PUBLIC_FRONT_URL } from '$env/static/public';
import { getAllPosts } from '$lib/blog/posts.js';

export async function GET() {
	const posts = getAllPosts();

	const blogUrls = posts
		.map(
			(post) => `
    <url>
        <loc>${PUBLIC_FRONT_URL}/blog/${post.slug}</loc>
        <lastmod>${post.date}T00:00:00+00:00</lastmod>
        <priority>0.7</priority>
    </url>`
		)
		.join('');

	return new Response(`
<?xml version="1.0" encoding="UTF-8" ?>
<urlset
	xmlns="https://www.sitemaps.org/schemas/sitemap/0.9"
	xmlns:xhtml="https://www.w3.org/1999/xhtml"
	xmlns:mobile="https://www.google.com/schemas/sitemap-mobile/1.0"
	xmlns:news="https://www.google.com/schemas/sitemap-news/0.9"
	xmlns:image="https://www.google.com/schemas/sitemap-image/1.1"
	xmlns:video="https://www.google.com/schemas/sitemap-video/1.1"
>
    <url>
        <loc>${PUBLIC_FRONT_URL}</loc>
        <lastmod>2025-1-1T21:42:13+00:00</lastmod>
        <priority>1</priority>
    </url>
    <url>
        <loc>${PUBLIC_FRONT_URL}/blog</loc>
        <lastmod>${new Date().toISOString()}</lastmod>
        <priority>0.8</priority>
    </url>${blogUrls}
</urlset>
		`.trim(),
		{
			headers: {
				'Content-Type': 'application/xml'
			}
		}
	);
}
