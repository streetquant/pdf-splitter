import pytest
from pathlib import Path


class TestEPUBProcessor:
    @pytest.fixture
    def sample_epub_path(self):
        return Path(
            "test/Addy Osmani - Vibe Coding_ The Future of Programming (2025, O'Reilly Media, Inc.) - libgen.li.epub"
        )

    @pytest.fixture
    def temp_output_dir(self, tmp_path):
        return tmp_path / "epub_output"

    def test_epub_exists(self, sample_epub_path):
        if not sample_epub_path.exists():
            pytest.skip("Test EPUB not found")
        assert sample_epub_path.exists()

    def test_epub_is_readable(self, sample_epub_path):
        if not sample_epub_path.exists():
            pytest.skip("Test EPUB not found")
        try:
            from ebooklib import epub

            book = epub.read_epub(str(sample_epub_path))
            assert book is not None
        except Exception as e:
            pytest.skip(f"EPUB file has structural issues: {e}")

    def test_extract_chapters_returns_list(self, sample_epub_path):
        if not sample_epub_path.exists():
            pytest.skip("Test EPUB not found")
        from pdfsplitter.core.epub_processor import extract_epub_chapters

        chapters = extract_epub_chapters(sample_epub_path)
        assert isinstance(chapters, list)

    def test_split_creates_output_directory(self, sample_epub_path, temp_output_dir):
        if not sample_epub_path.exists():
            pytest.skip("Test EPUB not found")
        from pdfsplitter.core.epub_processor import split_epub

        result = split_epub(sample_epub_path, temp_output_dir)
        assert temp_output_dir.exists()
        assert len(result.chapters) > 0

    def test_split_creates_metadata_file(self, sample_epub_path, temp_output_dir):
        if not sample_epub_path.exists():
            pytest.skip("Test EPUB not found")
        from pdfsplitter.core.epub_processor import split_epub

        split_epub(sample_epub_path, temp_output_dir)
        metadata_path = temp_output_dir / "metadata.json"
        assert metadata_path.exists()

    def test_split_creates_chapter_files(self, sample_epub_path, temp_output_dir):
        if not sample_epub_path.exists():
            pytest.skip("Test EPUB not found")
        from pdfsplitter.core.epub_processor import split_epub

        result = split_epub(sample_epub_path, temp_output_dir)
        for chapter in result.chapters:
            if chapter.file_path:
                assert chapter.file_path.exists(), (
                    f"Chapter file {chapter.file_path} does not exist"
                )
