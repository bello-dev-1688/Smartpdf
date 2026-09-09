from pathlib import Path
from uuid import uuid4

class DocumentLifecycle:
    def save_working(self, document, directory):
        target = Path(directory) / 'working.pdf'
        temp = target.with_name(f'working.{uuid4().hex}.tmp.pdf')
        try:
            document.save(temp)
            document.close()
            temp.replace(target)
        finally:
            temp.unlink(missing_ok=True)
