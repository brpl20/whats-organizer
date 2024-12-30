from subprocess import CalledProcessError, Popen, run, PIPE, STDOUT
from re import search
from typing import Callable, Dict, Optional
from sys import platform

from sanitize import sanitize_path


def convert_to(folder: str, source:str, timeout:Optional[int]=None) -> str:
    folder = sanitize_path(folder)
    source = sanitize_path(source)
    command = [
        libreoffice_exec(),
        '--headless',
        '--convert-to',
        'pdf',
        '--outdir',
        folder,
        source,
    ]


    process = Popen(command, stdout=PIPE, stderr=STDOUT, text=True)
    stdout, stderr = process.communicate()
    if int(process.returncode or 0):
        print(f'failed to convert document to pdf {source}')
        return ''
    
    filename = search('-> (.*?) using filter', stdout)

    if filename is None: 
        raise LibreOfficeError(stdout)

    return filename.group(1) or ""

libreoffice_path: Dict[str, str] = {
    'darwin': '/Applications/LibreOffice.app/Contents/MacOS/soffice',
    'linux': 'libreoffice',
}

get_platform: Callable[
    [], str
] = lambda: platform if platform in dict.keys(libreoffice_path) else 'linux'
# TODO: Provide support for more platforms
libreoffice_exec: Callable[
    [], str
] = lambda: libreoffice_path[get_platform()]


class LibreOfficeError(Exception):
    def __init__(self, output: str):
        self.output = output
