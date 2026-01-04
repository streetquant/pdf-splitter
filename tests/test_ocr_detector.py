import pytest
from pathlib import Path


def is_likely_searchable(text, min_chars=50):
    cleaned = "".join(c for c in text if c.isalnum() or c.isspace())
    return len(cleaned.strip()) >= min_chars


class TestIsLikelySearchable:
    def test_garbled_text(self):
        text = "xxxxxxxxxxxxx xxxxxxxxxxxxx garbled text xxxxxxxxxxxxx"
        assert is_likely_searchable(text, min_chars=10) is True
        text_short = "xxx xxx"
        assert is_likely_searchable(text_short, min_chars=10) is False

    def test_clean_text(self):
        text = (
            "This is a normal paragraph with meaningful content for testing purposes."
        )
        assert is_likely_searchable(text) is True

    def test_empty_text(self):
        assert is_likely_searchable("") is False

    def test_short_text(self):
        assert is_likely_searchable("Hi") is False

    def test_whitespace_only(self):
        assert is_likely_searchable("   \n\n  ") is False

    def test_unicode_text(self):
        text = "Hello world! This is a test document with enough characters to pass."
        assert is_likely_searchable(text) is True


class TestUtils:
    def test_sanitize_filename(self):
        from pdfsplitter.utils.file_ops import sanitize_filename

        assert sanitize_filename("test/file:name") == "test_file_name"
        assert sanitize_filename("  valid name  ") == "valid name"

    def test_ensure_directory(self, tmp_path):
        from pdfsplitter.utils.file_ops import ensure_directory

        new_dir = tmp_path / "new" / "nested"
        result = ensure_directory(new_dir)
        assert result.exists()
        assert result.is_dir()

    def test_detect_file_type_pdf(self, tmp_path):
        from pdfsplitter.utils.file_ops import detect_file_type

        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b"%PDF-1.4")
        assert detect_file_type(test_file) == "pdf"

    def test_detect_file_type_epub(self, tmp_path):
        from pdfsplitter.utils.file_ops import detect_file_type

        test_file = tmp_path / "test.epub"
        test_file.write_bytes(b"PK\x03\x04")
        assert detect_file_type(test_file) == "epub"
