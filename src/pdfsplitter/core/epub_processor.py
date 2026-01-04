import json
from pathlib import Path
from ebooklib import epub
from bs4 import BeautifulSoup
from .models import Chapter, SplitResult
from ..utils import get_logger

logger = get_logger(__name__)


def extract_epub_chapters(epub_path: Path) -> list[Chapter]:
    chapters = []

    try:
        book = epub.read_epub(str(epub_path))

        def process_navpoint(navpoint, section_num=None, depth=0):
            if isinstance(navpoint, tuple):
                nav, children = navpoint
                title = getattr(nav, "title", str(nav)) or f"Section {section_num}"
                href = getattr(nav, "href", None)

                if depth < 2:
                    chapters.append(
                        Chapter(
                            title=title.strip(),
                            start_page=len(chapters),
                            end_page=len(chapters),
                            file_path=None,
                        )
                    )

                if children:
                    for i, child in enumerate(children):
                        process_navpoint(
                            child,
                            f"{section_num}.{i + 1}" if section_num else str(i + 1),
                            depth + 1,
                        )

        for i, navpoint in enumerate(book.toc):
            process_navpoint(navpoint, str(i + 1))

        if not chapters:
            for i, item in enumerate(book.get_items()):
                if item.get_type() == epub.ITEM_DOCUMENT:
                    title = item.get_name()
                    chapters.append(
                        Chapter(
                            title=f"Section {i + 1}",
                            start_page=i,
                            end_page=i,
                            file_path=None,
                        )
                    )

    except Exception as e:
        logger.error(f"Error extracting EPUB chapters: {e}")

    return chapters


def split_epub(epub_path: Path, output_dir: Path) -> SplitResult:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    chapters = extract_epub_chapters(epub_path)

    if not chapters:
        chapters = [
            Chapter(
                title="Complete Document",
                start_page=0,
                end_page=0,
                file_path=output_dir / "chapter_01.xhtml",
            )
        ]

    for i, chapter in enumerate(chapters):
        chapter_path = output_dir / f"chapter_{i + 1:02d}.xhtml"
        chapter.file_path = chapter_path
        chapter_path.write_text(
            f"<html><body><h1>{chapter.title}</h1><p>Extracted from {epub_path.name}</p></body></html>"
        )

    metadata = {
        "original_file": str(epub_path),
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

    return SplitResult(
        original=epub_path, chapters=chapters, pretext=None, posttext=None
    )
