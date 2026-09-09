import pymupdf
from pdf_form_filler.core.coordinates import normalized_to_pdf

def test_normalized_coordinates():
    rect = normalized_to_pdf(pymupdf.Rect(0,0,600,800), .1, .2, .5, .1)
    assert rect.x0 == 60 and rect.y0 == 160 and rect.x1 == 360 and abs(rect.y1-240) < 1e-9
