import re
import json
from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass
from PyPDF2 import PdfReader, PdfWriter
import fitz
from .models import Chapter, SplitResult
from ..constants import (
    CHAPTER_PATTERNS,
    CHAPTER_IGNORE_PATTERNS,
    TOC_HEADER_PATTERNS,
    TOC_ENTRY_PATTERNS,
    POSTTEXT_MARKER_PATTERNS,
    MIN_CHAPTER_TITLE_LENGTH,
    MIN_PAGE_CONTENT_LENGTH,
    MIN_PAGES_BETWEEN_CHAPTERS,
)
from ..utils import get_logger

logger = get_logger(__name__)


@dataclass
class ChapterCandidate:
    page_num: int
    title: str
    confidence: float = 0.8
    source: str = "text"
    end_page: Optional[int] = None


@dataclass
class TOCEntry:
    level: int
    title: str
    page_num: int
    raw_title: str = ""
    source: str = "pdf_toc"


CHAPTER_ONLY_PATTERN = re.compile(r"^CHAPTER\s+(\d+)$", re.IGNORECASE)


def is_ignored_pattern(text: str) -> bool:
    for pattern in CHAPTER_IGNORE_PATTERNS:
        if pattern.match(text.strip()):
            return True
    return False


def get_page_content_length(page_text: str) -> int:
    cleaned = "".join(c for c in page_text if c.isalnum() or c.isspace())
    return len(cleaned.strip())


def is_chapter_only(title: str) -> bool:
    return bool(CHAPTER_ONLY_PATTERN.match(title.strip()))


def extract_toc_from_pdf(pdf_path: Path) -> List[TOCEntry]:
    toc_entries = []

    try:
        with fitz.open(pdf_path) as doc:
            pdf_toc = doc.get_toc()

            if pdf_toc:
                for entry in pdf_toc:
                    level, title, page_num = entry[:3]
                    toc_entries.append(
                        TOCEntry(
                            level=level,
                            title=title,
                            page_num=page_num - 1,
                            source="pdf_toc",
                        )
                    )

            if not toc_entries:
                toc_entries = find_toc_by_text_search(doc)

    except Exception as e:
        logger.error(f"Error extracting TOC: {e}")

    return toc_entries


def find_toc_by_text_search(doc) -> List[TOCEntry]:
    toc_entries = []

    for page_num, page in enumerate(doc):
        text = page.get_text("text")
        if not text:
            continue

        first_lines = " ".join(text.split("\n")[:5]).lower()

        is_toc_page = any(
            pattern.search(first_lines) for pattern in TOC_HEADER_PATTERNS
        )

        if is_toc_page:
            lines = page.get_text("text").split("\n")

            for line in lines:
                line = line.strip()
                if len(line) < 5 or len(line) > 150:
                    continue

                for pattern in TOC_ENTRY_PATTERNS:
                    match = pattern.match(line)
                    if match:
                        try:
                            chapter_num = int(match.group(1))
                            chapter_title = match.group(2).strip()
                            referenced_page = int(match.group(3))

                            toc_entries.append(
                                TOCEntry(
                                    level=1,
                                    title=f"CHAPTER {chapter_num}",
                                    page_num=referenced_page - 1,
                                    raw_title=chapter_title,
                                    source="text_toc",
                                )
                            )
                            break
                        except (ValueError, IndexError):
                            continue

    return toc_entries


def detect_page_offset(toc_entries: List[TOCEntry], pdf_path: Path) -> int:
    with fitz.open(pdf_path) as doc:
        total_pages = len(doc)

        if not toc_entries:
            return 0

        first_chapter = next(
            (
                e
                for e in toc_entries
                if "chapter" in e.title.lower() and re.search(r"\d+", e.title)
            ),
            None,
        )

        if not first_chapter:
            return 0

        toc_page = first_chapter.page_num

        chapter_pattern = re.compile(
            r"^\s*CHAPTER\s+(\d+)\b", re.IGNORECASE | re.MULTILINE
        )

        for search_page in range(toc_page, min(toc_page + 15, total_pages)):
            page = doc[search_page]
            text = page.get_text("text")

            for line in text.split("\n")[:15]:
                line = line.strip()
                match = chapter_pattern.match(line)
                if match:
                    chapter_num = int(match.group(1))
                    expected_match = re.search(r"(\d+)", first_chapter.title)
                    if expected_match:
                        expected_num = int(expected_match.group(1))

                        if chapter_num == expected_num:
                            offset = search_page - toc_page
                            logger.info(f"Detected page offset: {offset}")
                            return offset

    return 0


def apply_offset_to_toc(toc_entries: List[TOCEntry], offset: int) -> List[TOCEntry]:
    if offset == 0:
        return toc_entries

    adjusted = []
    for entry in toc_entries:
        adjusted_entry = TOCEntry(
            level=entry.level,
            title=entry.title,
            page_num=entry.page_num + offset,
            raw_title=entry.raw_title,
            source=entry.source,
        )
        adjusted.append(adjusted_entry)

    return adjusted


def detect_chapters_by_text(doc) -> List[ChapterCandidate]:
    candidates = []

    chapter_pattern = re.compile(
        r"^\s*(CHAPTER\s+\d+)\s*$", re.IGNORECASE | re.MULTILINE
    )

    for page_num, page in enumerate(doc):
        text = page.get_text("text")
        if not text:
            continue

        lines = text.split("\n")

        for line in lines[:12]:
            line = line.strip()

            if len(line) < 5 or len(line) > 60:
                continue

            if is_ignored_pattern(line):
                continue

            match = chapter_pattern.match(line)
            if match:
                title = match.group(1).strip().upper()

                page_content_length = get_page_content_length(text)
                confidence = 0.85
                if page_content_length > 500:
                    confidence += 0.1

                candidates.append(
                    ChapterCandidate(
                        page_num=page_num,
                        title=title,
                        confidence=min(confidence, 1.0),
                        source="text",
                    )
                )

    return candidates


def merge_toc_with_text_detection(
    toc_entries: List[TOCEntry], text_candidates: List[ChapterCandidate]
) -> List[ChapterCandidate]:
    merged = []
    used_pages = set()

    for toc_entry in toc_entries:
        toc_page = toc_entry.page_num

        text_match = next((c for c in text_candidates if c.page_num == toc_page), None)

        if text_match:
            merged.append(text_match)
            used_pages.add(toc_page)
        else:
            if is_chapter_only(toc_entry.title):
                merged.append(
                    ChapterCandidate(
                        page_num=toc_page,
                        title=toc_entry.title,
                        confidence=0.95,
                        source="toc",
                    )
                )
                used_pages.add(toc_page)

    for candidate in text_candidates:
        if candidate.page_num not in used_pages:
            merged.append(candidate)
            used_pages.add(candidate.page_num)

    return sorted(merged, key=lambda x: x.page_num)


def deduplicate_candidates(
    candidates: List[ChapterCandidate],
    min_pages_between: int = MIN_PAGES_BETWEEN_CHAPTERS,
) -> List[ChapterCandidate]:
    if not candidates:
        return candidates

    sorted_candidates = sorted(candidates, key=lambda c: c.page_num)

    deduplicated = []
    last_page = -min_pages_between

    for candidate in sorted_candidates:
        if candidate.page_num - last_page >= min_pages_between:
            deduplicated.append(candidate)
            last_page = candidate.page_num

    return deduplicated


def detect_chapter_boundaries(
    candidates: List[ChapterCandidate], total_pages: int, pdf_path: Path
) -> List[ChapterCandidate]:
    with fitz.open(pdf_path) as doc:
        for i, candidate in enumerate(candidates):
            if candidate.end_page is not None:
                continue

            if i + 1 < len(candidates):
                candidate.end_page = candidates[i + 1].page_num - 1
            else:
                posttext_start = detect_posttext_start_page(doc, candidate.page_num)
                if posttext_start > candidate.page_num:
                    candidate.end_page = posttext_start - 1
                else:
                    candidate.end_page = total_pages - 1

    return candidates


def detect_posttext_start_page(doc, start_page: int) -> int:
    total_pages = len(doc)

    for page_num in range(start_page + 10, total_pages):
        page = doc[page_num]
        text = page.get_text("text")
        lines = text.split("\n")

        for line in lines[:10]:
            line_stripped = line.strip()
            if not line_stripped:
                continue

            for pattern in POSTTEXT_MARKER_PATTERNS:
                if pattern.search(line_stripped):
                    return page_num

            references_pattern = re.compile(
                r"^(?:REFERENCES|BIBLIOGRAPHY|APPENDIX|INDEX|NOTES|GLOSSARY|AFTERWORD|EPILOGUE)\s*$",
                re.IGNORECASE | re.MULTILINE,
            )
            if references_pattern.match(line_stripped):
                return page_num

    return total_pages


def is_posttext_section(title: str) -> bool:
    title_lower = title.lower().strip()

    posttext_markers = [
        "appendix",
        "references",
        "bibliography",
        "index",
        "acknowledgments",
        "notes",
        "glossary",
        "afterword",
        "epilogue",
        "name index",
        "subject index",
    ]

    for marker in posttext_markers:
        if marker in title_lower:
            return True

    return False


def is_posttext_start(text: str, page_num: int, last_chapter_start: int) -> bool:
    lines = text.split("\n")

    for line in lines[:10]:
        line_stripped = line.strip()
        if not line_stripped:
            continue

        for pattern in POSTTEXT_MARKER_PATTERNS:
            if pattern.search(line_stripped):
                return True

        references_pattern = re.compile(
            r"^(?:REFERENCES|BIBLIOGRAPHY|APPENDIX|INDEX|NOTES|GLOSSARY|AFTERWORD|EPILOGUE)\s*$",
            re.IGNORECASE | re.MULTILINE,
        )
        if references_pattern.match(line_stripped):
            return True

    meaningful_lines = [l for l in text.split("\n") if len(l.strip()) > 30]
    if len(meaningful_lines) < 3 and page_num - last_chapter_start > 15:
        return True

    return False


def detect_posttext(pdf_path: Path, last_chapter_end: int) -> tuple[int, int]:
    with fitz.open(pdf_path) as doc:
        total_pages = len(doc)

        for page_num in range(last_chapter_end + 1, total_pages):
            page = doc[page_num]
            text = page.get_text("text")

            if is_posttext_start(text, page_num, last_chapter_end):
                logger.info(f"Detected posttext starting at page {page_num}")
                return (page_num, total_pages - 1)

        return (last_chapter_end + 1, total_pages - 1)


def split_pdf(pdf_path: Path, output_dir: Path) -> SplitResult:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Processing: {pdf_path}")

    candidates = []

    with fitz.open(pdf_path) as doc:
        toc_entries = extract_toc_from_pdf(pdf_path)

        if toc_entries:
            logger.info(f"Found {len(toc_entries)} TOC entries")

            toc_chapters = [e for e in toc_entries if is_chapter_only(e.title)]
            logger.info(f"Found {len(toc_chapters)} CHAPTER entries in TOC")

            offset = detect_page_offset(toc_chapters, pdf_path)

            if offset > 0:
                toc_chapters = apply_offset_to_toc(toc_chapters, offset)
                logger.info(f"Applied page offset: {offset}")

            text_candidates = detect_chapters_by_text(doc)

            if text_candidates:
                logger.info(
                    f"Found {len(text_candidates)} text-based chapter candidates"
                )
                candidates = merge_toc_with_text_detection(
                    toc_chapters, text_candidates
                )
            else:
                candidates = [
                    ChapterCandidate(
                        page_num=entry.page_num,
                        title=entry.title,
                        confidence=0.95,
                        source="toc",
                    )
                    for entry in toc_chapters
                ]
        else:
            logger.info("No TOC found, using text-based detection")
            candidates = detect_chapters_by_text(doc)

    candidates = deduplicate_candidates(candidates)
    logger.info(f"Found {len(candidates)} chapter candidates after deduplication")

    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)

    if not candidates:
        chapter_path = output_dir / "chapter_01.pdf"
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        writer.write(chapter_path)

        chapter = Chapter(
            title="Complete Document",
            start_page=0,
            end_page=total_pages - 1,
            file_path=chapter_path,
        )

        metadata = {
            "original_file": str(pdf_path),
            "total_pages": total_pages,
            "chapters": [
                {
                    "title": chapter.title,
                    "start_page": chapter.start_page,
                    "end_page": chapter.end_page,
                    "file_path": str(chapter_path),
                }
            ],
        }
        (output_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))

        return SplitResult(
            original=pdf_path, chapters=[chapter], pretext=None, posttext=None
        )

    candidates = detect_chapter_boundaries(candidates, total_pages, pdf_path)
    candidates = sorted(candidates, key=lambda c: c.page_num)

    chapters = []
    first_chapter_page = candidates[0].page_num

    if first_chapter_page > 0:
        pretext_path = output_dir / "pretext.pdf"
        writer = PdfWriter()
        for i in range(first_chapter_page):
            writer.add_page(reader.pages[i])
        writer.write(pretext_path)

        chapters.append(
            Chapter(
                title="Pre-text",
                start_page=0,
                end_page=first_chapter_page - 1,
                file_path=pretext_path,
            )
        )

    chapter_num = 1
    for i, candidate in enumerate(candidates):
        start_page = candidate.page_num
        end_page = candidate.end_page if candidate.end_page else start_page

        if end_page < start_page:
            end_page = start_page

        chapter_path = output_dir / f"chapter_{chapter_num:02d}.pdf"
        writer = PdfWriter()
        for p in range(start_page, end_page + 1):
            writer.add_page(reader.pages[p])
        writer.write(chapter_path)

        chapters.append(
            Chapter(
                title=candidate.title,
                start_page=start_page,
                end_page=end_page,
                file_path=chapter_path,
            )
        )
        chapter_num += 1

    last_chapter = chapters[-1] if chapters else None
    if last_chapter and last_chapter.end_page < total_pages - 1:
        posttext_start, posttext_end = detect_posttext(pdf_path, last_chapter.end_page)

        if posttext_start <= posttext_end and posttext_start < total_pages:
            posttext_path = output_dir / "posttext.pdf"
            writer = PdfWriter()
            for i in range(posttext_start, posttext_end + 1):
                writer.add_page(reader.pages[i])
            writer.write(posttext_path)

            chapters.append(
                Chapter(
                    title="Post-text",
                    start_page=posttext_start,
                    end_page=posttext_end,
                    file_path=posttext_path,
                )
            )

    metadata = {
        "original_file": str(pdf_path),
        "total_pages": total_pages,
        "chapters": [
            {
                "title": c.title,
                "start_page": c.start_page,
                "end_page": c.end_page,
                "file_path": str(c.file_path) if c.file_path else None,
            }
            for c in chapters
        ],
    }
    (output_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))

    pretext = chapters[0] if chapters and chapters[0].title == "Pre-text" else None
    posttext = chapters[-1] if chapters and chapters[-1].title == "Post-text" else None

    logger.info(f"Successfully split into {len(chapters)} sections")

    return SplitResult(
        original=pdf_path, chapters=chapters, pretext=pretext, posttext=posttext
    )
