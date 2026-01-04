from .ocr_detector import needs_ocr
from .pdf_processor import split_pdf
from .epub_processor import split_epub
from .models import Chapter, SplitResult

__all__ = [
    "needs_ocr",
    "split_pdf",
    "split_epub",
    "Chapter",
    "SplitResult",
]
