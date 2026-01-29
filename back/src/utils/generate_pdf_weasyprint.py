"""
PDF generation using WeasyPrint + Jinja2 templates.
Replaces the Playwright-based PDF generator.
"""

import os
import base64
from io import BytesIO
from typing import Callable
from urllib.parse import urlparse

from jinja2 import Environment, FileSystemLoader
from PIL import Image
import weasyprint


TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), '..', 'templates')
MEDIA_BASE_DIR = './zip_tests/'
MAX_IMAGE_PX = 800


def _find_file_in_zip_tests(filename: str) -> str | None:
    """Walk zip_tests/ to locate a file by its relative path or basename."""
    for root, _dirs, files in os.walk(MEDIA_BASE_DIR):
        candidate = os.path.join(root, filename)
        if os.path.isfile(candidate):
            return candidate
        # Also try just the basename in this directory
        basename = os.path.basename(filename)
        if basename in files:
            return os.path.join(root, basename)
    return None


def _resize_and_b64(filepath: str, max_px: int = MAX_IMAGE_PX) -> str:
    """Open an image, resize to max_px on longest side, return base64 data URI."""
    try:
        img = Image.open(filepath)
        img.thumbnail((max_px, max_px), Image.LANCZOS)
        buf = BytesIO()
        fmt = 'PNG' if filepath.lower().endswith('.png') else 'JPEG'
        img.save(buf, format=fmt)
        b64 = base64.b64encode(buf.getvalue()).decode('ascii')
        mime = 'image/png' if fmt == 'PNG' else 'image/jpeg'
        return f'data:{mime};base64,{b64}'
    except Exception as e:
        print(f"[PDF] Failed to encode image {filepath}: {e}")
        return ''


def _url_to_local_path(url: str) -> str | None:
    """Convert a /media/... URL to a local file path in zip_tests/."""
    parsed = urlparse(url)
    path = parsed.path
    # Strip /media/ prefix
    if '/media/' in path:
        relative = path.split('/media/', 1)[1]
    else:
        relative = path.lstrip('/')
    return _find_file_in_zip_tests(relative)


def _get_ext(filename: str) -> str:
    return (filename.rsplit('.', 1)[-1] if '.' in filename else '').lower()


def _get_filename(path: str) -> str:
    return os.path.basename(path) if path else ''


def _classify_media(filename: str) -> str:
    ext = _get_ext(filename)
    if ext in ('jpg', 'jpeg', 'png', 'gif'):
        return 'image'
    if ext == 'opus':
        return 'audio'
    if ext == 'mp4':
        return 'video'
    if ext in ('docx', 'docm', 'doc', 'odt'):
        return 'docx'
    return 'other'


def _format_time(time_str: str) -> str:
    """Remove seconds if present (HH:MM:SS -> HH:MM)."""
    if not time_str:
        return ''
    parts = time_str.split(':')
    if len(parts) == 3:
        return f'{parts[0]}:{parts[1]}'
    return time_str


def _get_side(is_apple: bool, msg_id: int) -> str:
    """Determine sent/received side matching frontend logic."""
    sides = ['left', 'right'] if is_apple else ['right', 'left']
    idx = (msg_id or 1) - 1
    if idx < 0 or idx >= len(sides):
        idx = 0
    return 'sent' if sides[idx] == 'right' else 'received'


def _preprocess_messages(messages: list[dict], is_apple: bool, notify_callback: Callable[[str], None]) -> list[dict]:
    """Enrich messages with base64 media and template-friendly fields."""
    notify_callback('Preparando midias para PDF')
    enriched = []

    for msg in messages:
        m = dict(msg)  # shallow copy
        m['_side'] = _get_side(is_apple, m.get('ID', 1))
        m['_time_short'] = _format_time(m.get('Time', ''))
        m['_filename'] = _get_filename(m.get('FileAttached', '') or '')
        m['_media_type'] = None
        m['_b64'] = ''
        m['_pdf_pages'] = []

        file_attached = m.get('FileAttached')
        if file_attached:
            links = m.get('links', [])
            # Check if this is a PDF with page images
            if links and len(links) >= 2 and links[1] == 'pdf':
                m['_media_type'] = 'pdf_pages'
                page_b64s = []
                # links structure: [pdf_url, 'pdf', page1_url, orientation1, page2_url, ...]
                i = 2
                while i < len(links):
                    page_url = links[i]
                    # Skip orientation string
                    local = _url_to_local_path(str(page_url))
                    if local:
                        b64 = _resize_and_b64(local)
                        if b64:
                            page_b64s.append(b64)
                    i += 2  # skip url + orientation
                m['_pdf_pages'] = page_b64s
            else:
                media_type = _classify_media(file_attached)
                m['_media_type'] = media_type

                if media_type == 'image':
                    local = _find_file_in_zip_tests(file_attached)
                    if local:
                        m['_b64'] = _resize_and_b64(local)

        enriched.append(m)

    return enriched


def generate_pdf(messages: list[dict], is_apple: bool, notify_callback: Callable[[str], None]) -> bytes:
    """
    Generate a PDF from chat messages using Jinja2 + WeasyPrint.

    Args:
        messages: List of message dicts from the /process endpoint.
        is_apple: Whether the conversation is from an Apple device.
        notify_callback: Function to send status updates.

    Returns:
        PDF file contents as bytes.
    """
    notify_callback('Preparando impressao')

    enriched = _preprocess_messages(messages, is_apple, notify_callback)

    notify_callback('Gerando HTML')

    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=True)
    template = env.get_template('chat_pdf.html')

    html_string = template.render(
        messages=enriched,
        is_apple=is_apple,
        message_count=len(messages),
    )

    notify_callback('Gerando Arquivo PDF')

    pdf_bytes = weasyprint.HTML(string=html_string).write_pdf()

    return pdf_bytes
