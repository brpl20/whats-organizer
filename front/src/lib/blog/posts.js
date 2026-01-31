import matter from 'gray-matter';
import { marked } from 'marked';

/**
 * @typedef {object} PostMeta
 * @property {string} title
 * @property {string} slug
 * @property {string} date
 * @property {string} description
 * @property {string} author
 */

/**
 * @typedef {object} Post
 * @property {PostMeta} meta
 * @property {string} html
 */

/**
 * Load all blog posts from the content directory.
 * @returns {PostMeta[]}
 */
export function getAllPosts() {
	const modules = import.meta.glob('/src/content/posts/*.md', {
		eager: true,
		query: '?raw',
		import: 'default'
	});

	/** @type {PostMeta[]} */
	const posts = [];

	for (const [, raw] of Object.entries(modules)) {
		const { data } = matter(/** @type {string} */ (raw));
		posts.push(/** @type {PostMeta} */ (data));
	}

	// Sort by date descending
	posts.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());

	return posts;
}

/**
 * Load a single blog post by slug.
 * @param {string} slug
 * @returns {Post | null}
 */
export function getPostBySlug(slug) {
	const modules = import.meta.glob('/src/content/posts/*.md', {
		eager: true,
		query: '?raw',
		import: 'default'
	});

	for (const [path, raw] of Object.entries(modules)) {
		const { data, content } = matter(/** @type {string} */ (raw));
		if (data.slug === slug) {
			return {
				meta: /** @type {PostMeta} */ (data),
				html: marked.parse(content)
			};
		}
	}

	return null;
}
