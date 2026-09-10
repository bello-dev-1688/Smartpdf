````markdown
# SmartPDF

SmartPDF is a general-purpose PDF form filler built with **FastAPI** and **PyMuPDF**.

It supports three types of documents:

- Native fillable PDF forms
- Scanned PDF forms
- Image-based forms

## Status

SmartPDF is currently a **backend-first MVP** with a separate web frontend.

### Implemented

- Native PDF field discovery
- Native text field filling
- Native checkbox filling
- Native signature-field detection
- Native signature image upload
- PDF uploads
- PNG/JPG/JPEG/BMP/WEBP image uploads
- Image-to-PDF conversion
- Manual field mapping for scanned/image forms
- Normalized `0..1` field coordinates
- Text, checkbox, and signature mapping
- Field movement, resizing, and deletion
- PDF page rendering
- Explicit PDF export
- Separate source and working documents

## Architecture

```text
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
````

The backend is frontend-agnostic. Browser, mouse, touch, and device-specific interactions belong to the frontend.

## Repository Structure

```text
Smartpdf/
├── backend/
│   ├── main.py
│   ├── dev_cli.py
│   ├── requirements.txt
│   ├── docs/
│   └── pdf_form_filler/
└── frontend/
```

### Important Backend Areas

```text
api/          FastAPI routes
core/         Models, coordinates, and errors
documents/    Storage and document lifecycle
fields/       Field mapping and values
forms/        Native and image form logic
pdf/          PDF handling
services/     Application orchestration
signatures/   Signature handling
```

## Setup

From the `backend/` directory:

```powershell
pip install -r requirements.txt
python main.py
```

API documentation:

[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## MVP Workflow

```text
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
```

## Important Design Principle

SmartPDF is intentionally **general-purpose**.

It is designed to support:

1. Native PDF forms
2. Scanned PDF forms
3. Image-based forms

The implementation must not become dependent on a specific form such as W-8BEN.

Normalized coordinates are used for scanned and image-based field mapping so that field positions remain independent of screen size, browser viewport, or input device.

## Development

The backend can be developed and tested independently of the frontend.

When extending SmartPDF, preserve:

* The service-layer architecture
* The normalized coordinate contract
* Source/working document separation
* The frontend/backend boundary

Detailed technical documentation is available in:

```text
backend/docs/architecture.md
backend/docs/image-form-interaction.md
```

```

