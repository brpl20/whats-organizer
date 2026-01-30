import { getAllPosts } from '$lib/blog/posts.js';

export function load() {
	const posts = getAllPosts();
	return { posts };
}
