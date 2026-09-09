from pdf_form_filler.core.errors import FieldNotFoundError, InvalidFieldError
from pdf_form_filler.core.models import FieldType
from pdf_form_filler.forms.native import NativeForm
from pdf_form_filler.pdf.document import PDFDocument
from pdf_form_filler.documents.lifecycle import DocumentLifecycle


class FieldValueManager:
    def __init__(self, storage):
        self.storage = storage
        self.lifecycle = DocumentLifecycle()

    def set(self, document_id, field_id, value):
        document = PDFDocument(self.storage.working(document_id))
        try:
            # PyMuPDF widgets are bound to the page object returned by
            # page.widgets(). Keep that page alive while calling widget.update().
            # Discovering the widget first and updating it later can produce:
            # "Annot is not bound to a page".
            for page_number in range(document.page_count):
                page = document.get_page(page_number)
                widgets = page.widgets() or []

                for index, widget in enumerate(widgets):
                    current_id = f"native_{page_number}_{index}"

                    if current_id != field_id:
                        continue

                    field_type = NativeForm.WIDGET_TYPES.get(
                        widget.field_type,
                        FieldType.UNKNOWN,
                    )

                    if field_type == FieldType.TEXT:
                        widget.field_value = str(value)

                    elif field_type == FieldType.CHECKBOX:
                        widget.field_value = bool(value)

                    else:
                        raise InvalidFieldError(
                            "This native field type is not supported yet."
                        )

                    # IMPORTANT:
                    # Update while the page is still alive and the widget
                    # is still bound to that page.
                    widget.update()

                    result = {
                        "id": current_id,
                        "name": widget.field_name or f"field_{index}",
                        "field_type": field_type.value,
                        "page_number": page_number,
                        "value": widget.field_value,
                    }

                    directory = self.storage.directory(document_id)
                    self.lifecycle.save_working(document, directory)

                    return result

            # If it is not a native field, check manually mapped image fields.
            data = self.storage.read_image_fields(document_id)

            if field_id not in data:
                raise FieldNotFoundError(field_id)

            if data[field_id]["field_type"] == "signature":
                raise InvalidFieldError(
                    "Use the signature endpoint for signature fields."
                )

            data[field_id]["value"] = value
            self.storage.write_image_fields(document_id, data)

            return data[field_id]

        finally:
            try:
                document.close()
            except Exception:
                pass