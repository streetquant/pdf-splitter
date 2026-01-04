from pathlib import Path
import re

PROJECT_NAME = "pdfsplitter"
VERSION = "1.0.0"

CHAPTER_PATTERNS = [
    re.compile(r"^CHAPTER\s+\d+$", re.IGNORECASE | re.MULTILINE),
    re.compile(r"^CHAPTER\s+[IVXLCDM]+$", re.IGNORECASE | re.MULTILINE),
    re.compile(r"^Part\s+\d+$", re.IGNORECASE | re.MULTILINE),
    re.compile(r"^PART\s+\d+$", re.IGNORECASE | re.MULTILINE),
    re.compile(r"^Part\s+[IVXLCDM]+$", re.IGNORECASE | re.MULTILINE),
    re.compile(r"^PART\s+[IVXLCDM]+$", re.IGNORECASE | re.MULTILINE),
]

CHAPTER_IGNORE_PATTERNS = [
    re.compile(r"^\d+\.\s+[A-Z]\.$"),
    re.compile(r"^\d+\.\s+[A-Z]\s+\d+$"),
    re.compile(r"^\d+\.\s+[A-Z]\.\s+\d+$"),
    re.compile(r"^\d+\s+\w{1,2}$"),
    re.compile(r"^\d+\.\s+\w{1,3}$"),
]

TOC_HEADER_PATTERNS = [
    re.compile(r"^table\s+of\s+contents$", re.IGNORECASE),
    re.compile(r"^contents$", re.IGNORECASE),
    re.compile(r"^chapters$", re.IGNORECASE),
    re.compile(r"^index\s+of\s+chapters$", re.IGNORECASE),
]

TOC_ENTRY_PATTERNS = [
    re.compile(r"^(\d+)\.\s+(.+?)\.+\s+(\d+)$"),
    re.compile(r"^(\d+)\.\s+(.+?)\s+(\d+)$"),
    re.compile(r"^Chapter\s+(\d+)[:\s]+(.+?)\s+page\s+(\d+)$", re.IGNORECASE),
    re.compile(r"^(\d+)\s+(.+?)\s+\.\.\+\.?\s+(\d+)$"),
]

POSTTEXT_MARKER_PATTERNS = [
    re.compile(r"^references?\s*$", re.IGNORECASE),
    re.compile(r"^bibliography\s*$", re.IGNORECASE),
    re.compile(r"^appendix\s+[a-z]?\s*$", re.IGNORECASE),
    re.compile(r"^index\s*$", re.IGNORECASE),
    re.compile(r"^acknowledgments?\s*$", re.IGNORECASE),
    re.compile(r"^notes?\s*$", re.IGNORECASE),
    re.compile(r"^glossary\s*$", re.IGNORECASE),
    re.compile(r"^afterword\s*$", re.IGNORECASE),
    re.compile(r"^epilogue\s*$", re.IGNORECASE),
]

MIN_TEXT_CHARS = 50
MAX_SAMPLE_CHARS = 3000
SAMPLE_PAGES = 3
MIN_CHAPTER_TITLE_LENGTH = 5
MIN_PAGE_CONTENT_LENGTH = 200
MIN_PAGES_BETWEEN_CHAPTERS = 3
