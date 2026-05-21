"""PDF text extraction using pdfplumber."""

import pdfplumber


def extract_text_from_pdf(pdf_path: str) -> str:
    pages = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                pages.append(f"[Page {i + 1}]\n{text}")
    return "\n\n".join(pages)


def extract_pages(pdf_path: str) -> list[dict]:
    result = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            result.append({"page_number": i + 1, "text": text, "char_count": len(text)})
    return result


def is_valid_pdf(pdf_path: str) -> bool:
    try:
        with pdfplumber.open(pdf_path) as pdf:
            if not pdf.pages:
                return False
            first_page = pdf.pages[0].extract_text()
            return bool(first_page and len(first_page.strip()) > 50)
    except Exception:
        return False
