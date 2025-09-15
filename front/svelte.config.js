import adapter from '@sveltejs/adapter-node';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';
import {randomUUID} from 'crypto'

/** @type {import('@sveltejs/kit').Config} */
const config = {
  preprocess: vitePreprocess(),
  
  kit: {
    adapter: adapter(),
    version: {
      // Busts cache for cloudflare, nginx, browser, etc on each build
      name: randomUUID({  disableEntropyCache: true }),
    },
    // Desabilita proteção de CSRF para o backend
    csrf: {
      checkOrigin: false,
    },
  }
};

export default config;