# Future Review Items

Items identified during the `feat/weasyprint-pdf` branch review that are not blocking deployment but should be addressed later.

---

## 1. `_get_side()` logic (`generate_pdf_weasyprint.py:94-100`)

The function determines sent/received using a 2-element array with `(msg_id - 1)` as index. Any msg_id > 2 falls to `idx = 0` default. Verify this produces correct side assignment for all messages in long conversations.

## 2. Silent failures for missing media (`generate_pdf_weasyprint.py:140-143`)

If image files aren't found in `zip_tests/`, the PDF renders with empty `_b64` fields. Users receive a PDF with missing images and no indication that anything is wrong. Consider adding logging or a summary of skipped files.

## 3. Synchronous PDF generation (`app.py:130`)

`generate_pdf()` runs synchronously on the Flask request thread. For large conversations with many images, this could block for a significant time. The `ThreadPoolExecutor` is defined (line 64) but unused. Could be used if load becomes an issue.

## 4. `sock_send` used as PDF callback (`app.py:130`)

The `sock_send` lambda emits to SocketIO globally, but the PDF endpoint is a regular HTTP POST. There is no guarantee a WebSocket is connected for that specific client. Progress messages may go to wrong clients or nowhere.

## 5. File lookup performance (`generate_pdf_weasyprint.py:22-32`)

`_find_file_in_zip_tests()` walks the entire `zip_tests/` directory tree for every image. No caching. For conversations with many images and many files on disk, this is O(messages * files). Consider building a file index on first call.

## 6. Large PDF file sizes

All images are embedded inline as base64 (no external references, no compression beyond 800px resize). A conversation with 100+ images could produce a 30-50MB PDF.

## 7. No input validation on `/download-pdf`

The `messages` field from the JSON body is used without schema validation. Malformed messages (missing `ID`, `Time`, `FileAttached`) would cause runtime errors caught by the generic try/catch.
