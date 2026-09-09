import pymupdf

def normalized_to_pdf(page_rect, x, y, width, height):
    if not (0 <= x <= 1 and 0 <= y <= 1 and 0 < width <= 1 and 0 < height <= 1):
        raise ValueError("Normalized coordinates must be between 0 and 1.")
    if x + width > 1 or y + height > 1:
        raise ValueError("Normalized field rectangle must stay inside the page.")
    return pymupdf.Rect(page_rect.x0+x*page_rect.width, page_rect.y0+y*page_rect.height, page_rect.x0+(x+width)*page_rect.width, page_rect.y0+(y+height)*page_rect.height)

def pdf_to_normalized(page_rect, rect):
    return {"x":(rect.x0-page_rect.x0)/page_rect.width,"y":(rect.y0-page_rect.y0)/page_rect.height,"width":rect.width/page_rect.width,"height":rect.height/page_rect.height}
