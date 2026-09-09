import os
import tempfile
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from pdf_form_filler.services.document_service import DocumentService


router = APIRouter()

service = DocumentService()


def cleanup_file(path: str):
    try:
        Path(path).unlink(missing_ok=True)
    except PermissionError:
        pass


@router.post("/documents/{document_id}/export")
def export(document_id: str):
    fd, filename = tempfile.mkstemp(suffix=".pdf")

    # Windows keeps a file locked while its file descriptor is open.
    # Close it before PyMuPDF tries to write the PDF.
    os.close(fd)

    output = Path(filename)

    try:
        service.export(document_id, output)

        return FileResponse(
            path=output,
            media_type="application/pdf",
            filename=f"{document_id}.pdf",
            background=BackgroundTask(
                cleanup_file,
                str(output),
            ),
        )

    except Exception:
        cleanup_file(str(output))
        raise