from os import getenv
from json import dumps
from typing import Callable, TypeAlias, cast

from werkzeug.datastructures import FileStorage
from playwright.async_api import async_playwright, PdfMargins
from asyncio import sleep

JSON: TypeAlias = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None

playwright_headless_env = getenv("HEADLESS", "True") == "True"
front_url_env = getenv("FRONT_URL", "https://whatsorganizer.com.br")

async def print_page_pdf( file: FileStorage, notify_callback: Callable[[str], None] ) -> bytes:
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=playwright_headless_env,
            args=['--allow-file-access-from-files'],
            # https://github.com/microsoft/playwright/issues/4585
            executable_path='/usr/bin/google-chrome-stable'
        )
        notify_callback("Carregando Chat")
        page = await browser.new_page()
        # page.add_init_script(script=f"window.messages = {messages}")
        await page.goto(front_url_env)

        injector_media_input = page.locator('[data-testid="playwright-inject-media"]')
        
        for el in (injector_media_input,):
            await el.wait_for(state='attached', timeout=5000)
            await el.evaluate(f"""(e) => e.setAttribute('style', 'display: block');""")
            await el.wait_for(state='visible', timeout=5000)
            
        notify_callback('Preparando Impressão')
        
        file_buffer = file.stream.read()
        await injector_media_input.set_input_files([{"name": file.filename, "mimeType": "application/zip", "buffer": file_buffer}])

        chat = page.locator('[data-testid="playwright-chat"]')
        await chat.wait_for(timeout=10000)
        
        notify_callback('Carregando Mídias')
        
        unloaded_imgs = page.locator('//img')
        if unloaded_imgs:
            await unloaded_imgs.evaluate_all("elements => elements.forEach(e => e.scrollIntoView())")
            for image in await unloaded_imgs.element_handles():
                await image.evaluate("async (el) => el.complete || new Promise(resolve => el.onload = resolve)")
        
        while await page.locator('[data-rendered="false"]').first.count():
            await sleep(.2)

        #await page.emulate_media(media="print")
        await sleep(.2)
        
        notify_callback("Gerando Arquivo PDF")

        pdf_bytes = await page.pdf(
            format="A4",
            print_background=True,
            scale=1.2,
            margin=cast(PdfMargins, {
                **{y: '30' for y in ('top', 'bottom')},
                **{x: '5' for x in ('right', 'left')},
            }),
        )
        await browser.close()
    return pdf_bytes