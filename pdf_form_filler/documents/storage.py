from pathlib import Path
import json
import shutil
from uuid import uuid4

from pdf_form_filler.core.errors import DocumentNotFoundError

class DocumentStorage:
    def __init__(self, root='data/documents'):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def directory(self, document_id):
        path = self.root / document_id
        if not path.exists():
            raise DocumentNotFoundError(document_id)
        return path

    def create(self, source_path):
        document_id = uuid4().hex
        directory = self.root / document_id
        directory.mkdir()
        shutil.copyfile(source_path, directory / 'source.pdf')
        shutil.copyfile(source_path, directory / 'working.pdf')
        return document_id

    def source(self, document_id): return self.directory(document_id) / 'source.pdf'
    def working(self, document_id): return self.directory(document_id) / 'working.pdf'
    def image_fields(self, document_id): return self.directory(document_id) / 'image_fields.json'
    def read_image_fields(self, document_id):
        path = self.image_fields(document_id)
        return json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}

    def write_image_fields(self, document_id, data):
        path = self.image_fields(document_id)
        temp = path.with_name(f'{path.stem}.{uuid4().hex}.tmp')
        try:
            temp.write_text(json.dumps(data, indent=2), encoding='utf-8')
            temp.replace(path)
        finally:
            temp.unlink(missing_ok=True)
