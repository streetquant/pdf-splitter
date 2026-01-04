from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class Chapter:
    title: str
    start_page: int
    end_page: int
    file_path: Optional[Path] = None


@dataclass
class SplitResult:
    original: Path
    chapters: list[Chapter]
    pretext: Optional[Chapter] = None
    posttext: Optional[Chapter] = None


@dataclass
class OCRResult:
    needs_ocr: bool
    confidence: float
    reasoning: str = ""
