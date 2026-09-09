# Backend Architecture

## Boundary
The backend owns PDF processing and document state. It does not know about mouse events, touch events, HTML, React, Android UI, or Tkinter.

## Native forms
PyMuPDF widgets are the source of truth. The backend dynamically discovers widget types and exposes their page, rectangle, name, type, and current value.

## Image/scanned forms
There is intentionally no automatic rectangle detector in the backend. A future frontend lets the user draw a rectangle. The frontend sends normalized coordinates in the range 0..1. The backend converts them to PDF points and stores the mapping.

This makes the same API work on desktop and mobile browsers regardless of viewport size, zoom, pixel density, or input device.

## Document lifecycle
1. Upload PDF.
2. Store an untouched `source.pdf` and a separate `working.pdf`.
3. Inspect and modify the working copy.
4. Export a new PDF.
5. Never overwrite `source.pdf`.

## Current API
- `GET /health`
- `POST /documents`
- `GET /documents/{document_id}`
- `GET /documents/{document_id}/fields`
- `POST /documents/{document_id}/fields`
- `PUT /documents/{document_id}/fields/{field_id}`
- `POST /documents/{document_id}/fields/{field_id}/signature`
- `GET /documents/{document_id}/pages/{page_number}/render`
- `POST /documents/{document_id}/export`

## Future frontend responsibilities
- PDF/page viewer.
- Mouse/touch rectangle drawing for image forms.
- Normalized coordinate calculation.
- Text input overlays.
- Checkbox interaction.
- Signature selection/upload UI.
- Zoom and page navigation.

The frontend should not implement PDF mutation logic itself.
