import pymupdf
from pdf_form_filler.core.models import Field, FieldType

class NativeForm:
    """Discovers fields directly from PDF widget metadata."""
    WIDGET_TYPES={
        pymupdf.PDF_WIDGET_TYPE_TEXT: FieldType.TEXT,
        pymupdf.PDF_WIDGET_TYPE_CHECKBOX: FieldType.CHECKBOX,
        pymupdf.PDF_WIDGET_TYPE_RADIOBUTTON: FieldType.RADIO,
        pymupdf.PDF_WIDGET_TYPE_COMBOBOX: FieldType.COMBO,
        pymupdf.PDF_WIDGET_TYPE_LISTBOX: FieldType.LIST,
        pymupdf.PDF_WIDGET_TYPE_SIGNATURE: FieldType.SIGNATURE,
    }
    def __init__(self,document): self.document=document
    def discover_fields(self):
        fields=[]
        for page_number in range(self.document.page_count):
            widgets = self.document.get_page(page_number).widgets() or []
            for index, widget in enumerate(widgets):
                fields.append(self._field(widget, page_number, index))
        return fields
    def _field(self,widget,page_number,index):
        field_type=self.WIDGET_TYPES.get(widget.field_type,FieldType.UNKNOWN)
        return Field(id=f'native_{page_number}_{index}',name=widget.field_name or f'field_{index}',
                     field_type=field_type,page_number=page_number,rect=pymupdf.Rect(widget.rect),
                     value=widget.field_value,widget=widget)
