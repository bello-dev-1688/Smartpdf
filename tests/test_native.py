from pdf_form_filler.pdf.document import PDFDocument
from pdf_form_filler.forms.native import NativeForm
def test_sample_native_fields():
    doc=PDFDocument("sample.pdf")
    try:
        fields=NativeForm(doc).discover_fields(); assert len(fields)>0; assert any(f.is_signature for f in fields)
    finally: doc.close()
