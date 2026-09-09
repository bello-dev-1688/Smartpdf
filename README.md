# PDF Form Filler — Backend

This is the backend-first refactor. The production client will be a web frontend built later. The backend is also directly testable through `dev_cli.py` and the Python service layer.

## Architecture
- FastAPI HTTP API
- PyMuPDF PDF engine
- Native AcroForm widget discovery
- Manual mapping for scanned/image forms
- Normalized 0..1 coordinates for device/viewport independence
- Signature image placement
- File-based document workspace for development

## Run
```powershell
pip install -r requirements.txt
python main.py
```
Then open `/docs` on the local server.

## No frontend testing
```powershell
python dev_cli.py inspect sample.pdf
pytest
```
The CLI uses the same `DocumentService` used by FastAPI.

## Scanned form contract
The future frontend draws a rectangle using mouse or touch and sends normalized coordinates: `x`, `y`, `width`, `height` in the range 0..1. The backend converts those coordinates to PDF points. No screen pixels are stored.
