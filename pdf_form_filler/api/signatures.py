from pathlib import Path
import tempfile
from fastapi import APIRouter, File, UploadFile
from pdf_form_filler.api.dependencies import service
from pdf_form_filler.api.errors import to_http
router=APIRouter(prefix='/documents/{document_id}/fields')
@router.post('/{field_id}/signature')
async def upload_signature(document_id,field_id,file:UploadFile=File(...)):
    suffix=Path(file.filename or '').suffix.lower()
    with tempfile.NamedTemporaryFile(delete=False,suffix=suffix) as temp:
        temp.write(await file.read()); path=Path(temp.name)
    try: return service.upload_signature(document_id,field_id,path)
    except Exception as error: raise to_http(error)
    finally: path.unlink(missing_ok=True)
