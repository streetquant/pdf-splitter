import pytest
from pathlib import Path


class TestPDFProcessor:
    @pytest.fixture
    def sample_pdf_path(self):
        return Path(
            "test/[Mihaly_Csikszentmihalyi,_Eugene_Halton]_The_Meani(b-ok.cc).pdf"
        )

    @pytest.fixture
    def temp_output_dir(self, tmp_path):
        return tmp_path / "output"

    def test_pdf_exists(self, sample_pdf_path):
        if not sample_pdf_path.exists():
            pytest.skip("Test PDF not found")
        assert sample_pdf_path.exists()

    def test_pdf_is_readable(self, sample_pdf_path):
        if not sample_pdf_path.exists():
            pytest.skip("Test PDF not found")
        import fitz

        with fitz.open(sample_pdf_path) as doc:
            assert len(doc) > 0

    def test_detect_chapters_returns_list(self, sample_pdf_path):
        if not sample_pdf_path.exists():
            pytest.skip("Test PDF not found")
        import fitz
        from pdfsplitter.core.pdf_processor import detect_chapters_by_text

        with fitz.open(sample_pdf_path) as doc:
            candidates = detect_chapters_by_text(doc)
        assert isinstance(candidates, list)

    def test_split_creates_output_directory(self, sample_pdf_path, temp_output_dir):
        if not sample_pdf_path.exists():
            pytest.skip("Test PDF not found")
        from pdfsplitter.core.pdf_processor import split_pdf

        result = split_pdf(sample_pdf_path, temp_output_dir)
        assert temp_output_dir.exists()
        assert len(result.chapters) > 0

    def test_split_creates_metadata_file(self, sample_pdf_path, temp_output_dir):
        if not sample_pdf_path.exists():
            pytest.skip("Test PDF not found")
        from pdfsplitter.core.pdf_processor import split_pdf

        split_pdf(sample_pdf_path, temp_output_dir)
        metadata_path = temp_output_dir / "metadata.json"
        assert metadata_path.exists()

    def test_split_creates_chapter_files(self, sample_pdf_path, temp_output_dir):
        if not sample_pdf_path.exists():
            pytest.skip("Test PDF not found")
        from pdfsplitter.core.pdf_processor import split_pdf

        result = split_pdf(sample_pdf_path, temp_output_dir)
        for chapter in result.chapters:
            if chapter.file_path:
                assert chapter.file_path.exists()
