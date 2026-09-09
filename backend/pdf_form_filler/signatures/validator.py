from pathlib import Path
from PIL import Image
class SignatureValidator:
    SUPPORTED_EXTENSIONS={'.png','.jpg','.jpeg','.bmp','.webp'}
    def validate(self, image_path):
        p=Path(image_path)
        if p.suffix.lower() not in self.SUPPORTED_EXTENSIONS: raise ValueError('Unsupported signature image format.')
        if not p.exists(): raise FileNotFoundError('Signature image could not be found.')
        with Image.open(p) as image: image.verify()
        return p
