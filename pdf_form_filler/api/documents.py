from pathlib import Path
import tempfile
from fastapi import APIRouter, File, UploadFile, HTTPException
from pdf_form_filler.api.dependencies import service
from pdf_form_filler.api.errors import to_http
router=APIRouter(prefix='/documents')
@router.post('')
async def upload_document(file: UploadFile=File(...)):
    if not file.filename or not file.filename.lower().endswith('.pdf'): raise HTTPException(400,'Only PDF files are supported.')
    with tempfile.NamedTemporaryFile(delete=False,suffix='.pdf') as temp:
        temp.write(await file.read()); path=Path(temp.name)
    try: return service.inspect(service.upload(path,file.filename))
    except Exception as error: raise to_http(error)
    finally: path.unlink(missing_ok=True)
@router.get('/{document_id}')
def inspect_document(document_id):
    try: return service.inspect(document_id)
    except Exception as error: raise to_http(error)
