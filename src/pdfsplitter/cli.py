import subprocess
from pathlib import Path
import click
from .config import settings
from .core import needs_ocr, split_pdf, split_epub
from .utils import Cache, setup_logging, get_logger
import sys

logger = get_logger(__name__)


def run_ocr(input_path: Path, output_path: Path) -> bool:
    try:
        result = subprocess.run(
            [
                "ocrmypdf",
                "--deskew",
                "--clean",
                "--optimize",
                "3",
                "-q",
                str(input_path),
                str(output_path),
            ],
            capture_output=True,
            text=True,
            timeout=settings.OCR_TIMEOUT,
        )

        return result.returncode == 0
    except subprocess.TimeoutExpired:
        logger.error("OCR timed out")
        return False
    except Exception as e:
        logger.error(f"OCR failed: {e}")
        return False


@click.command()
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(file_okay=False, path_type=Path),
    default=None,
    help="Output directory (default: <input>_output)",
)
@click.option("--cache/--no-cache", default=True, help="Use cache for OCR decisions")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def main(input_file: Path, output_dir: Path, cache: bool, verbose: bool):
    setup_logging("DEBUG" if verbose else "INFO")

    if output_dir is None:
        output_dir = input_file.parent / f"{input_file.stem}_output"
    output_dir = Path(output_dir)

    logger.info(f"Processing: {input_file}")
    logger.info(f"Output directory: {output_dir}")

    cache_obj = Cache(settings.CACHE_DIR) if cache else None

    try:
        if input_file.suffix.lower() == ".pdf":
            needs, reasoning = needs_ocr(input_file, cache_obj)
            logger.info(f"OCR decision: {reasoning}")

            if needs:
                logger.info("Scanned PDF detected, running OCR...")
                ocr_path = input_file.with_stem(f"{input_file.stem}_ocr")
                if run_ocr(input_file, ocr_path):
                    result = split_pdf(ocr_path, output_dir)
                    try:
                        ocr_path.unlink()
                    except OSError:
                        pass
                else:
                    logger.warning("OCR failed, proceeding with original file")
                    result = split_pdf(input_file, output_dir)
            else:
                result = split_pdf(input_file, output_dir)

        elif input_file.suffix.lower() == ".epub":
            result = split_epub(input_file, output_dir)

        else:
            raise click.UsageError(f"Unsupported file type: {input_file.suffix}")

        logger.info(f"Successfully processed {len(result.chapters)} chapters")

        click.echo(f"\n✓ Processing complete!")
        click.echo(f"  Input: {input_file.name}")
        click.echo(f"  Output: {output_dir}")
        click.echo(f"  Chapters: {len(result.chapters)}")

        for i, chapter in enumerate(result.chapters):
            click.echo(f"    {i + 1:02d}. {chapter.title}")

    except Exception as e:
        logger.error(f"Processing failed: {e}")
        raise click.ClickException(str(e))


if __name__ == "__main__":
    main()
