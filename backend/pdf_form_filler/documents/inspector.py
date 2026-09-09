from pdf_form_filler.forms.native import NativeForm
from pdf_form_filler.pdf.document import PDFDocument
from pdf_form_filler.core.models import FormType
from pdf_form_filler.core.coordinates import pdf_to_normalized

class DocumentInspector:
    def inspect(self, working_path, image_fields):
        document = PDFDocument(working_path)
        try:
            native = NativeForm(document).discover_fields()
            fields = [self._native_dict(document, f) for f in native]
            fields.extend(image_fields.values())
            return {'form_type': FormType.NATIVE.value if native else FormType.IMAGE.value,
                    'page_count': document.page_count, 'fields': fields}
        finally:
            document.close()

    def _native_dict(self, document, field):
        page = document.get_page(field.page_number)
        return {'id': field.id, 'name': field.name, 'field_type': field.field_type.value,
                'page_number': field.page_number, 'value': field.value,
                'rect': {'x': field.rect.x0, 'y': field.rect.y0,
                         'width': field.rect.width, 'height': field.rect.height},
                'normalized': pdf_to_normalized(page.rect, field.rect)}
