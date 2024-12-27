from os import getenv
from json import dumps
from typing import TypeAlias

from werkzeug.datastructures import FileStorage
from playwright.async_api import async_playwright
from asyncio import sleep

JSON: TypeAlias = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None

async def print_page( file: FileStorage, messages: JSON ) -> bytes:
    playwright_headless = getenv("HEADLESS", "True") == "True"

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=playwright_headless,
            args=['--allow-file-access-from-files'],
            # https://github.com/microsoft/playwright/issues/4585
            executable_path='/usr/bin/google-chrome-stable'
        )
        page = await browser.new_page()
        # page.add_init_script(script=f"window.messages = {messages}")
        await page.goto("http://whatsorganizer.com.br")

        injector_media_input = page.locator('[data-testid="playwright-inject-media"]')
        injector_chat_input = page.locator('[data-testid="playwright-inject-chat"]')
        
        for el in (injector_media_input, injector_chat_input):
            await el.wait_for(state='attached', timeout=5000)
            await el.evaluate(f"""(e) => e.setAttribute('style', 'display: block');""")
            await el.wait_for(state='visible', timeout=5000)
    
        await injector_chat_input.evaluate(f"""
            (e) => e.setAttribute('value', String('{dumps(messages)}'))
        """)
        await injector_chat_input.press('Enter')
        
        file_buffer = file.stream.read()
        await injector_media_input.set_input_files([{"name": file.filename, "mimeType": "application/zip", "buffer": file_buffer}])

        chat = page.locator('[data-testid="playwright-chat"]')
        await chat.wait_for(timeout=10000)
        
        
        unloaded_imgs = page.locator('//img')
        if unloaded_imgs:
            await unloaded_imgs.evaluate_all("elements => elements.forEach(e => e.scrollIntoView())")
            for image in await unloaded_imgs.element_handles():
                await image.evaluate("async (el) => el.complete || new Promise(resolve => el.onload = resolve)")
        
        while await page.locator('[data-rendered="false"]').first.count():
            await sleep(.2)

        #await page.emulate_media(media="print")
        await sleep(.2)

        pdf_bytes = await page.pdf(
            format="A4",
            print_background=True,
            scale=1.2,
            margin={
                **{y: '30' for y in ('top', 'bottom')},
                **{x: '5' for x in ('right', 'left')},
            },
        )
        await browser.close()
    return pdf_bytes