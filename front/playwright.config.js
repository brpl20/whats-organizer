const front_port = 1337;
const front_host = '127.0.0.1'
const front_url = `http://${front_host}:${front_port}`;

const back_port = 4242;
const back_host = '127.0.0.1'
const back_url = `http://${back_host}:${back_port}`;

/** @type {import('@playwright/test').PlaywrightTestConfig} */
const config = {
	webServer: [{
		command: `env PUBLIC_API_URL=${back_url} npm run build && \\
			env PORT=${front_port} node --env-file=.env build/index`,
		port: front_port,
		env: {
			PORT: front_port.toString(),
			HOST: front_host,
			ORIGIN: front_url
		}
	},
	{
		command: `env FLASK_PORT=${back_port} python3 -m app`,
		cwd: '../back',
		port: back_port,
		env: {
			PORT: back_port.toString(),
			HOST: back_host,
			ORIGIN: back_url
		}
	}
	],
	testDir: 'tests/e2e',
	testMatch: /(.+\.)?(test|spec)\.[jt]s/,
	fullyParallel: true,
	forbidOnly: !process.env.CI,
	retries: process.env.CI ? 2 : 0,
	workers: process.env.CI ? 1 : undefined,
	reporter: 'html',
	use: {
		baseURL: front_url,
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
			front_url
		}
	]
};

export default config;
