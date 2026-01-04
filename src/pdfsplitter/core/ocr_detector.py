import fitz
from pathlib import Path
import hashlib
from typing import Optional
from ..utils.cache import Cache
from ..utils.llm import analyze_for_ocr
from ..constants import MIN_TEXT_CHARS, MAX_SAMPLE_CHARS, SAMPLE_PAGES
from ..config import settings


def is_likely_searchable(text: str, min_chars: int = MIN_TEXT_CHARS) -> bool:
    cleaned = "".join(c for c in text if c.isalnum() or c.isspace())
    return len(cleaned.strip()) >= min_chars


def extract_text_sample(
    pdf_path: Path, page_num: int, max_chars: int = MAX_SAMPLE_CHARS
) -> str:
    try:
        with fitz.open(pdf_path) as doc:
            if page_num < len(doc):
                return doc[page_num].get_text("text")[:max_chars]
    except Exception:
        pass
    return ""


def needs_ocr(pdf_path: Path, cache: Optional[Cache] = None) -> tuple[bool, str]:
    doc_hash = hashlib.sha256(pdf_path.read_bytes()).hexdigest()[:16]
    cache_key = f"ocr_{doc_hash}"

    if cache:
        cached = cache.get(cache_key)
        if cached is not None:
            return cached.get(
                "needs_ocr", False
            ), f"Cache hit: {cached.get('reasoning', '')}"

    try:
        with fitz.open(pdf_path) as doc:
            num_pages = len(doc)
            sample_pages = list(range(min(SAMPLE_PAGES, num_pages)))

            samples = []
            for page_num in sample_pages:
                text = doc[page_num].get_text("text")
                samples.append(f"[Page {page_num + 1}]:\n{text[:MAX_SAMPLE_CHARS]}")

            if all(is_likely_searchable(s) for s in samples):
                result = False
                reasoning = "Heuristic: all sample pages have sufficient clean text"

                if cache:
                    cache.set(cache_key, {"needs_ocr": result, "reasoning": reasoning})

                return result, reasoning

            llm_result, llm_reasoning = analyze_for_ocr(samples)

            if llm_result is not None:
                result = llm_result
                reasoning = f"{llm_reasoning}"
            else:
                result = any(len(s) > 10 for s in samples)
                reasoning = f"Fallback: {'text detected' if result else 'minimal text'}"

            if cache:
                cache.set(cache_key, {"needs_ocr": result, "reasoning": reasoning})

            return result, reasoning

    except Exception as e:
        return True, f"Error reading PDF: {str(e)}"
