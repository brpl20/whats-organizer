import { PUBLIC_FRONT_URL } from '$env/static/public';

export async function GET() {
	return new Response(`
User-agent: *
Disallow: 

Sitemap: ${PUBLIC_FRONT_URL}/sitemap.xml
    `.trim()
    );
}
