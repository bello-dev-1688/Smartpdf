# SmartPDF

SmartPDF is a general-purpose PDF form filler built with **FastAPI** and **PyMuPDF**. It supports native fillable PDFs, scanned PDFs, and image-based forms.

## Status

Backend-first MVP with a separate web frontend.

Implemented:
- Native PDF field discovery.
- Native text and checkbox filling.
- Native signature-field detection and signature upload.
- PDF and PNG/JPG/JPEG/BMP/WEBP uploads.
- Image-to-PDF conversion.
- Manual mapping for scanned/image forms.
- Normalized `0..1` coordinates.
- Mapped text, checkbox, and signature fields.
- Field move, resize, and delete.
- PDF page rendering.
- Explicit PDF export.
- Separate source and working documents.

## Architecture

Web Frontend
     |
     v
FastAPI API
     |
     v
DocumentService
     |
     +--> Native Forms
     +--> Image Form Mapping
     +--> Field Values
     +--> Signatures
     +--> Rendering / Export
     |
     v
DocumentStorage
##
Repository

Smartpdf/
├── backend/
│   ├── main.py
│   ├── dev_cli.py
│   ├── requirements.txt
│   ├── docs/
│   └── pdf_form_filler/
└── frontend/

Important backend areas:

api/          FastAPI routes
core/         Models, coordinates, errors
documents/    Storage and document lifecycle
fields/       Field mapping and values
forms/        Native/image form logic
pdf/          PDF handling
services/     Application orchestration
signatures/   Signature handling

API documentation: http://127.0.0.1:8000/docs

MVP Workflow

Upload
  ↓
Inspect
  ↓
Native fields OR manual mapping
  ↓
Fill / Sign
  ↓
Save working state
  ↓
Explicit Export

NOTE: SmartPDF is intended to remain a general-purpose PDF form filler,in the sense that it can support native pdf forms, scanned pdf forms and image forms , not a form-specific implementation.