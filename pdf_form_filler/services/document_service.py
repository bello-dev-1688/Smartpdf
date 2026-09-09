from pathlib import Path
import shutil
import pymupdf

from pdf_form_filler.core.errors import FieldNotFoundError, InvalidFieldError
from pdf_form_filler.documents.storage import DocumentStorage
from pdf_form_filler.documents.inspector import DocumentInspector
from pdf_form_filler.fields.image_fields import ImageFieldManager
from pdf_form_filler.fields.values import FieldValueManager
from pdf_form_filler.forms.native import NativeForm
from pdf_form_filler.forms.image import ImageForm
from pdf_form_filler.pdf.document import PDFDocument
from pdf_form_filler.signatures.manager import SignatureManager


class DocumentService:
    """Coordinates document operations; detailed work lives in focused modules."""

    def __init__(self, storage_dir="data/documents"):
        self.storage = DocumentStorage(storage_dir)
        self.inspector = DocumentInspector()
        self.image_fields = ImageFieldManager(self.storage)
        self.values = FieldValueManager(self.storage)
        self.signatures = SignatureManager()

    def upload(self, source_path, filename=None):
        return self.storage.create(source_path)

    def inspect(self, document_id):
        result = self.inspector.inspect(
            self.storage.working(document_id),
            self.storage.read_image_fields(document_id),
        )
        result["document_id"] = document_id
        return result

    def list_fields(self, document_id):
        return self.inspect(document_id)["fields"]

    def add_image_field(
        self,
        document_id,
        field_id,
        page_number,
        field_type,
        x,
        y,
        width,
        height,
        name=None,
    ):
        return self.image_fields.create(
            document_id,
            field_id,
            page_number,
            field_type,
            x,
            y,
            width,
            height,
            name,
        )

    def update_image_field(self, document_id, field_id, **changes):
        return self.image_fields.update(document_id, field_id, changes)

    def delete_image_field(self, document_id, field_id):
        return self.image_fields.delete(document_id, field_id)

    def set_field_value(self, document_id, field_id, value):
        return self.values.set(document_id, field_id, value)

    def upload_signature(self, document_id, field_id, image_path):
        document = PDFDocument(self.storage.working(document_id))

        try:
            native = {
                field.id: field
                for field in NativeForm(document).discover_fields()
            }

            # Native PDF signature field
            if field_id in native:
                field = native[field_id]

                if not field.is_signature:
                    raise InvalidFieldError(
                        "Selected field is not a signature field."
                    )

                self.signatures.apply(document, field, image_path)

                # IMPORTANT:
                # Use document_id here, not the PDFDocument object.
                working_path = self.storage.working(document_id)
                temp_path = working_path.with_suffix(".tmp.pdf")

                document.save(temp_path)
                document.close()

                temp_path.replace(working_path)

                return {
                    "document_id": document_id,
                    "field_id": field_id,
                    "status": "signature_applied",
                }

            # Manually mapped image-form signature
            data = self.storage.read_image_fields(document_id)

            if field_id not in data:
                raise FieldNotFoundError(field_id)

            if data[field_id]["field_type"] != "signature":
                raise InvalidFieldError(
                    "Selected field is not a signature field."
                )

            path = self.signatures.validator.validate(image_path)

            suffix = path.suffix.lower()
            destination = (
                self.storage.directory(document_id)
                / f"signature_{field_id}{suffix}"
            )

            shutil.copyfile(path, destination)

            data[field_id]["signature_path"] = destination.name
            self.storage.write_image_fields(document_id, data)

            return {
                "document_id": document_id,
                "field_id": field_id,
                "status": "signature_stored",
            }

        finally:
            try:
                document.close()
            except Exception:
                pass

    def render_page(self, document_id, page_number, zoom=1.0):
        if zoom <= 0:
            raise ValueError("Zoom must be positive.")

        document = PDFDocument(self.storage.working(document_id))

        try:
            if not 0 <= page_number < document.page_count:
                raise ValueError("Invalid page number.")

            return document.get_page(page_number).get_pixmap(
                matrix=pymupdf.Matrix(zoom, zoom),
                alpha=False,
            ).tobytes("png")

        finally:
            document.close()

    def export(self, document_id, output_path):
        document = PDFDocument(self.storage.working(document_id))

        try:
            self._apply_image_fields(document, document_id)
            document.save(output_path)
        finally:
            document.close()

        return Path(output_path)

    def _apply_image_fields(self, document, document_id):
        for item in self.storage.read_image_fields(document_id).values():
            value = item.get("value")
            signature = item.get("signature_path")

            if value in (None, "", False) and not signature:
                continue

            field = ImageForm(document).create_field(
                item["id"],
                item["page_number"],
                item["field_type"],
                item["x"],
                item["y"],
                item["width"],
                item["height"],
                item.get("name"),
            )

            page = document.get_page(item["page_number"])

            if field.is_text:
                page.insert_textbox(
                    field.rect,
                    str(value),
                    fontsize=max(6, min(14, field.rect.height * 0.75)),
                    fontname="helv",
                    overlay=True,
                )

            elif field.is_checkbox and value:
                page.insert_textbox(
                    field.rect,
                    "✓",
                    fontsize=max(8, field.rect.height),
                    fontname="helv",
                    align=pymupdf.TEXT_ALIGN_CENTER,
                    overlay=True,
                )

            elif field.is_signature and signature:
                self.signatures.apply(
                    document,
                    field,
                    self.storage.directory(document_id) / signature,
                )