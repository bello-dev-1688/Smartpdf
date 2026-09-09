from pathlib import Path
import tempfile

from fastapi import APIRouter, File, UploadFile, HTTPException

from pdf_form_filler.api.dependencies import service
from pdf_form_filler.api.errors import to_http
from pdf_form_filler.documents.image_converter import is_supported_image


router = APIRouter(prefix="/documents")


@router.post("")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(400, "A file is required.")

    original_name = Path(file.filename).name
    suffix = Path(original_name).suffix.lower()

    if suffix != ".pdf" and not is_supported_image(Path(original_name)):
        raise HTTPException(
            400,
            "Unsupported document format. "
            "Upload a PDF or a PNG/JPG/JPEG/BMP/WEBP image.",
        )

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix,
    ) as temp:
        temp.write(await file.read())
        path = Path(temp.name)

    try:
        document_id = service.upload(path, original_name)
        return service.inspect(document_id)

    except Exception as error:
        raise to_http(error)

    finally:
        path.unlink(missing_ok=True)


@router.get("/{document_id}")
def inspect_document(document_id):
    try:
        return service.inspect(document_id)
    except Exception as error:
        raise to_http(error)
