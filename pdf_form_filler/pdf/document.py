from pathlib import Path
import pymupdf

class PDFDocument:
    def __init__(self, path):
        self.path=Path(path)
        if not self.path.exists(): raise FileNotFoundError(self.path)
        self.document=pymupdf.open(str(self.path))
    @property
    def page_count(self): return len(self.document)
    def get_page(self, page_number): return self.document[page_number]
    def save(self, output_path): self.document.save(str(output_path))
    def close(self): self.document.close()
