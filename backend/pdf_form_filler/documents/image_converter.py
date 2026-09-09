from pathlib import Path

import pymupdf
from PIL import Image, ImageOps


SUPPORTED_IMAGE_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".bmp",
    ".webp",
}


def is_supported_image(path: Path) -> bool:
    """Return True when the path points to a supported raster image."""
    return Path(path).suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS


def image_to_pdf(source_path: Path, output_path: Path) -> None:
    """
    Convert one raster image into a one-page PDF.

    The original image is never modified. EXIF orientation is respected.
    Image DPI metadata is used when available; otherwise 96 DPI is used.
    """
    source_path = Path(source_path)
    output_path = Path(output_path)

    if not is_supported_image(source_path):
        raise ValueError(
            "Unsupported image format. Supported formats: "
            "PNG, JPG, JPEG, BMP, WEBP."
        )

    with Image.open(source_path) as opened_image:
        image = ImageOps.exif_transpose(opened_image).convert("RGB")

        dpi = opened_image.info.get("dpi")

        try:
            dpi_x = float(dpi[0]) if dpi else 96.0
            dpi_y = float(dpi[1]) if dpi else 96.0
        except (TypeError, ValueError, IndexError):
            dpi_x = dpi_y = 96.0

        if dpi_x <= 0:
            dpi_x = 96.0

        if dpi_y <= 0:
            dpi_y = 96.0

        width_points = image.width * 72.0 / dpi_x
        height_points = image.height * 72.0 / dpi_y

        normalized_image = output_path.with_name(
            f"{output_path.stem}.{source_path.suffix.lstrip('.').lower()}.normalized.png"
        )

        document = None

        try:
            image.save(normalized_image, format="PNG")

            document = pymupdf.open()

            page = document.new_page(
                width=width_points,
                height=height_points,
            )

            page.insert_image(
                page.rect,
                filename=str(normalized_image),
            )

            document.save(output_path)

        finally:
            if document is not None:
                document.close()

            normalized_image.unlink(missing_ok=True)