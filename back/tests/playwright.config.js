// playwright.config.js
const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests',
  timeout: 120000, // File processing may take some time
  retries: 1,
  use: {
    headless: false,
    viewport: { width: 1280, height: 720 },
    launchOptions: {
      slowMo: 100,
    },
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
});
