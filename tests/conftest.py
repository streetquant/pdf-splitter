import pytest
from pathlib import Path


@pytest.fixture(scope="session")
def sample_pdf():
    path = Path("test/[Mihaly_Csikszentmihalyi,_Eugene_Halton]_The_Meani(b-ok.cc).pdf")
    if not path.exists():
        pytest.skip("Test PDF not found")
    return path


@pytest.fixture(scope="session")
def sample_epub():
    path = Path(
        "test/Addy Osmani - Vibe Coding_ The Future of Programming (2025, O'Reilly Media, Inc.) - libgen.li.epub"
    )
    if not path.exists():
        pytest.skip("Test EPUB not found")
    return path


@pytest.fixture
def temp_output_dir(tmp_path):
    return tmp_path / "output"
