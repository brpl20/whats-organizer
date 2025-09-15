from os import PathLike
from typing import Callable, TypeAlias

from werkzeug.datastructures import FileStorage

from print_page_pdf import print_page_pdf

JSON: TypeAlias = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None

async def save_page_pdf(file: FileStorage, notify_callback: Callable[[str], None], pdf_path: PathLike):
    pdf_bytes = await print_page_pdf(file, notify_callback)

    with open(pdf_path, 'wb') as pdf_write:
        pdf_write.write(pdf_bytes)
