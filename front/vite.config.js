import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
import tailwindcss from '@tailwindcss/vite';
import { configDefaults } from 'vitest/config'

export default defineConfig({
  resolve: process.env.VITEST
		? {
				conditions: ['browser']
			}
		: undefined,
  plugins: [sveltekit(), tailwindcss()],
  optimizeDeps: {
    include: ['mammoth']
  },
  build: {
    commonjsOptions: {
      include: [/node_modules/]
    }
  },
  test: {
    environment: 'jsdom',
    setupFiles: './tests/setup.js',
    exclude:[
      ...configDefaults.exclude, 
      'tests/e2e/*'
    ]
  },
});

// import { sveltekit } from '@sveltejs/kit/vite';
// import { defineConfig } from 'vitest/config';

// export default defineConfig({
// 	plugins: [sveltekit()],
// 	test: {
// 		include: ['src/**/*.{test,spec}.{js,ts}']
// 	}
// });
