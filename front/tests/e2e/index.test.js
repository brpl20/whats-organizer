import { expect, test } from '@playwright/test';
import fs from 'fs/promises';

test('Upload Chat', async ({ page }) => {
  await page.goto('/');
  
  const title = page.locator('h1')
  const uploadForm = page.getByTestId('file-upload-form')
  const uploadInput = uploadForm.locator('input[type="file"]')
  const submitBtn = page.getByTestId('submit-zip-btn')

  await expect(title).toBeVisible();
  await expect(uploadForm).toBeVisible();
  await expect(submitBtn).toBeVisible();
  
  const filePath = '/home/skid/My_Code/whats-organizer/tests/android-bruno/teste-audio-curto-uma-imagem.zip'
  const fileBuffer = await fs.readFile(filePath)

  await uploadInput.evaluate((input) => {
    input.setAttribute('style', 'display: block')
    input.removeAttribute('disabled')
  })
  
  const filename = 'teste-conversa.zip'
  await uploadInput.setInputFiles({
    name: filename,
    mimeType: 'application/zip',
    buffer: fileBuffer
  })

  await expect(page.locator(`text=${filename}`)).toBeVisible()

  const [response] = await Promise.all([
    page.waitForResponse(res => (
      res.request().method() === 'POST'
      && res.headers()['content-type']?.includes('application/json')
      && res.json().then(() => true).catch(() => false)
    )), submitBtn.click()])

  expect(response).toBeTruthy()

  for (const chatIndicator of ['toast-info', 'playwright-chat']) {
    await expect(page.getByTestId(chatIndicator)).toBeVisible()
  }

  for (const messageIndicator of ['audio', 'imagem', 'texto']) {
    await expect(page.locator(`[data-testid="${messageIndicator}"]`).first()).toBeVisible()
  }
})
