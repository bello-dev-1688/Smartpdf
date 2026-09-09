from fastapi import HTTPException
from pdf_form_filler.core.errors import DocumentNotFoundError, FieldNotFoundError, InvalidFieldError

def to_http(error):
    if isinstance(error, DocumentNotFoundError): return HTTPException(404, 'Document not found.')
    if isinstance(error, FieldNotFoundError): return HTTPException(404, 'Field not found.')
    if isinstance(error, (InvalidFieldError, ValueError)): return HTTPException(400, str(error))
    return HTTPException(500, str(error))
