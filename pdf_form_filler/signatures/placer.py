import pymupdf
from PIL import Image
from pdf_form_filler.signatures.validator import SignatureValidator
class SignaturePlacer:
    def __init__(self): self.validator=SignatureValidator()
    def apply(self, document, field, image_path):
        path=self.validator.validate(image_path)
        target=pymupdf.Rect(field.rect)
        with Image.open(path) as image: iw,ih=image.size
        ratio=min(target.width/iw,target.height/ih)
        width,height=iw*ratio,ih*ratio
        rect=pymupdf.Rect(target.x0+(target.width-width)/2,target.y0+(target.height-height)/2,
                          target.x0+(target.width+width)/2,target.y0+(target.height+height)/2)
        document.get_page(field.page_number).insert_image(rect,filename=str(path),keep_proportion=True,overlay=True)
