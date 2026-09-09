from fastapi import APIRouter
from pdf_form_filler.api.dependencies import service
from pdf_form_filler.api.errors import to_http
from pdf_form_filler.api.schemas import FieldValueUpdate, ImageFieldCreate, ImageFieldUpdate
router=APIRouter(prefix='/documents/{document_id}/fields')
@router.get('')
def list_fields(document_id):
    try: return {'fields':service.list_fields(document_id)}
    except Exception as error: raise to_http(error)
@router.post('')
def add_field(document_id,payload:ImageFieldCreate):
    try: return service.add_image_field(document_id,**payload.model_dump())
    except Exception as error: raise to_http(error)
@router.patch('/{field_id}')
def update_field(document_id,field_id,payload:ImageFieldUpdate):
    try: return service.update_image_field(document_id,field_id,**payload.model_dump(exclude_unset=True))
    except Exception as error: raise to_http(error)
@router.delete('/{field_id}')
def delete_field(document_id,field_id):
    try: return service.delete_image_field(document_id,field_id)
    except Exception as error: raise to_http(error)
@router.put('/{field_id}')
def set_value(document_id,field_id,payload:FieldValueUpdate):
    try: return service.set_field_value(document_id,field_id,payload.value)
    except Exception as error: raise to_http(error)
