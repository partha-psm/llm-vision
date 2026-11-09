"""Image object recognition and OCR using Ollama vision models."""

from pathlib import Path

import ollama
import pymupdf
from PIL import Image, UnidentifiedImageError

DEFAULT_MODEL = "gemma4:e2b"
ANALYSIS_PROMPT = """Analyze this image for object recognition and OCR.

List the clearly visible objects and briefly describe their positions or
relationships. Then transcribe all readable text exactly, preserving line
breaks where practical. Separate the object description and text transcription.
Do not guess at obscured or unreadable content; mark it as unclear.
"""


def analyze_image(
    image_path: str | Path,
    model: str = DEFAULT_MODEL,
) -> str:
    """Return object descriptions and OCR text for an image using Ollama."""
    path = Path(image_path).expanduser()
    if not path.is_file():
        raise FileNotFoundError(f"Image file does not exist: {path}")

    try:
        with Image.open(path) as image:
            image.verify()
    except (OSError, UnidentifiedImageError) as error:
        raise ValueError(f"Unable to read a valid image from: {path}") from error

    return _analyze_image(str(path.resolve()), model)


def analyze_pdf(
    pdf_path: str | Path,
    model: str = DEFAULT_MODEL,
) -> str:
    """Render each PDF page and return its object-recognition and OCR results."""
    path = Path(pdf_path).expanduser()
    if not path.is_file():
        raise FileNotFoundError(f"PDF file does not exist: {path}")

    try:
        document = pymupdf.open(path)
    except (pymupdf.FileDataError, OSError) as error:
        raise ValueError(f"Unable to read a valid PDF from: {path}") from error

    with document:
        if document.needs_pass:
            raise ValueError(f"PDF is password-protected: {path}")
        if document.page_count == 0:
            raise ValueError(f"PDF contains no pages: {path}")

        results: list[str] = []
        for page_number, page in enumerate(document, start=1):
            pixmap = page.get_pixmap(matrix=pymupdf.Matrix(2, 2), alpha=False)
            image_bytes = pixmap.tobytes("png")
            result = _analyze_image(image_bytes, model)
            results.append(f"Page {page_number}:\n{result}")

    return "\n\n".join(results)


def _analyze_image(image: str | bytes, model: str) -> str:
    response = ollama.generate(
        model=model,
        prompt=ANALYSIS_PROMPT,
        images=[image],
    )
    return response.response.strip()
