export async function GET() {
	return new Response(`
User-agent: *
Disallow: 

Sitemap: https://www.whatsorganizer.com/sitemap.xml
    `.trim()
    );
}
