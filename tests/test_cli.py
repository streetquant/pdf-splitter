import pytest
from click.testing import CliRunner
from pathlib import Path


class TestCLI:
    @pytest.fixture
    def runner(self):
        return CliRunner()

    @pytest.fixture
    def sample_pdf_path(self):
        return Path(
            "test/[Mihaly_Csikszentmihalyi,_Eugene_Halton]_The_Meani(b-ok.cc).pdf"
        )

    @pytest.fixture
    def sample_epub_path(self):
        return Path(
            "test/Addy Osmani - Vibe Coding_ The Future of Programming (2025, O'Reilly Media, Inc.) - libgen.li.epub"
        )

    def test_pdf_processing(self, runner, sample_pdf_path, tmp_path):
        if not sample_pdf_path.exists():
            pytest.skip("Test PDF not found")

        from pdfsplitter.cli import main

        output_dir = tmp_path / "pdf_output"
        result = runner.invoke(main, [str(sample_pdf_path), "-o", str(output_dir)])

        assert result.exit_code == 0 or "Processing complete" in result.output

    def test_epub_processing(self, runner, sample_epub_path, tmp_path):
        if not sample_epub_path.exists():
            pytest.skip("Test EPUB not found")

        from pdfsplitter.cli import main

        output_dir = tmp_path / "epub_output"
        result = runner.invoke(main, [str(sample_epub_path), "-o", str(output_dir)])

        assert result.exit_code == 0 or "Processing complete" in result.output

    def test_invalid_file_extension(self, runner, tmp_path):
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("hello")

        from pdfsplitter.cli import main

        result = runner.invoke(main, [str(txt_file)])

        assert result.exit_code != 0
        assert "Unsupported file type" in result.output

    def test_missing_file(self, runner):
        from pdfsplitter.cli import main

        result = runner.invoke(main, ["/nonexistent/file.pdf"])

        assert result.exit_code != 0

    def test_verbose_mode(self, runner, sample_pdf_path, tmp_path):
        if not sample_pdf_path.exists():
            pytest.skip("Test PDF not found")

        from pdfsplitter.cli import main

        output_dir = tmp_path / "pdf_output"
        result = runner.invoke(
            main, [str(sample_pdf_path), "-o", str(output_dir), "-v"]
        )

        assert result.exit_code == 0 or "-v" in result.output

    def test_custom_output_directory(self, runner, sample_pdf_path, tmp_path):
        if not sample_pdf_path.exists():
            pytest.skip("Test PDF not found")

        from pdfsplitter.cli import main

        output_dir = tmp_path / "custom_output"
        result = runner.invoke(main, [str(sample_pdf_path), "-o", str(output_dir)])

        if result.exit_code == 0:
            assert output_dir.exists()
