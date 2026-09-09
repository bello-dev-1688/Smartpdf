from pdf_form_filler.core.errors import FieldNotFoundError, InvalidFieldError
from pdf_form_filler.forms.image import ImageForm
from pdf_form_filler.pdf.document import PDFDocument

SUPPORTED = {'text', 'checkbox', 'signature'}

class ImageFieldManager:
    def __init__(self, storage): self.storage = storage

    def create(self, document_id, field_id, page_number, field_type, x, y, width, height, name=None):
        if field_type not in SUPPORTED: raise InvalidFieldError('Unsupported scanned-form field type.')
        data = self.storage.read_image_fields(document_id)
        if field_id in data: raise InvalidFieldError(f"Field '{field_id}' already exists.")
        document = PDFDocument(self.storage.working(document_id))
        try:
            ImageForm(document).create_field(field_id, page_number, field_type, x, y, width, height, name)
        finally: document.close()
        item = {'id': field_id, 'name': name or field_id, 'field_type': field_type,
                'page_number': page_number, 'x': x, 'y': y, 'width': width, 'height': height,
                'value': None, 'signature_path': None}
        data[field_id] = item
        self.storage.write_image_fields(document_id, data)
        return item

    def update(self, document_id, field_id, changes):
        data = self.storage.read_image_fields(document_id)
        if field_id not in data: raise FieldNotFoundError(field_id)
        allowed = {'name','page_number','field_type','x','y','width','height'}
        unknown = set(changes) - allowed
        if unknown: raise InvalidFieldError(f"Unsupported mapping properties: {', '.join(sorted(unknown))}.")
        item = dict(data[field_id]); item.update({k:v for k,v in changes.items() if v is not None})
        if item['field_type'] not in SUPPORTED: raise InvalidFieldError('Unsupported scanned-form field type.')
        document = PDFDocument(self.storage.working(document_id))
        try: ImageForm(document).create_field(field_id, item['page_number'], item['field_type'], item['x'], item['y'], item['width'], item['height'], item.get('name'))
        finally: document.close()
        data[field_id] = item; self.storage.write_image_fields(document_id, data); return item

    def delete(self, document_id, field_id):
        data = self.storage.read_image_fields(document_id)
        if field_id not in data: raise FieldNotFoundError(field_id)
        del data[field_id]; self.storage.write_image_fields(document_id, data)
        return {'field_id': field_id, 'status': 'deleted'}
