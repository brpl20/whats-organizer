const port = 1337;
const url = `http://localhost:${port}`;

/** @type {import('@playwright/test').PlaywrightTestConfig} */
const config = {
	webServer: {
		command: `npm run build && env PORT=${port} node --env-file=.env build/index`,
		port
	},
	testDir: 'tests/e2e',
	testMatch: /(.+\.)?(test|spec)\.[jt]s/,
	fullyParallel: true,
	forbidOnly: !process.env.CI,
	retries: process.env.CI ? 2 : 0,
	workers: process.env.CI ? 1 : undefined,
	reporter: 'html',
	use: {
		baseURL: url,
		trace: 'on-first-retry',
		headless: false,
		browserName: 'chromium',
		launchOptions: {
			args: [
				'--allow-file-access-from-files',
				'--disable-web-security',
				'--disable-features=VizDisplayCompositor',
				'--allow-file-access-from-files',
				'--allow-running-insecure-content',
				'--disable-site-isolation-trials'
			],
		}
	},
	projects: [
		{
			name: 'chromium',
			url
		}
	]
};

export default config;
