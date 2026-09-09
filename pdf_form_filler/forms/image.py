from pdf_form_filler.core.coordinates import normalized_to_pdf
from pdf_form_filler.core.models import Field, FieldType

class ImageForm:
    """Represents user-mapped fields on scanned/image forms."""
    def __init__(self,document): self.document=document
    def create_field(self,field_id,page_number,field_type,x,y,width,height,name=None):
        if not 0 <= page_number < self.document.page_count: raise ValueError('Invalid page number.')
        rect=normalized_to_pdf(self.document.get_page(page_number).rect,x,y,width,height)
        return Field(field_id,name or field_id,FieldType(field_type),page_number,rect,normalized=True)
