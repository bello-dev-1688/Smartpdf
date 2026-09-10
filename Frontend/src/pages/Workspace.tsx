import {
  useRef,
  useState,
} from "react";

import DocumentViewer from "../components/DocumentViewer";

import {
  exportDocument,
  inspectDocument,
  uploadDocument,
} from "../services/api";

import type { Field } from "../types/fields";

type DocumentInfo = {
  document_id: string;
  form_type: string;
  page_count: number;
  fields: Field[];
};

function normalizeFields(
  fields: Field[],
): Field[] {
  return fields.map((field) => {
    if (field.normalized) {
      return field;
    }

    const raw = field as Field & {
      x?: number;
      y?: number;
      width?: number;
      height?: number;
    };

    if (
      typeof raw.x === "number" &&
      typeof raw.y === "number" &&
      typeof raw.width === "number" &&
      typeof raw.height === "number"
    ) {
      return {
        ...field,
        normalized: {
          x: raw.x,
          y: raw.y,
          width: raw.width,
          height: raw.height,
        },
      };
    }

    return field;
  });
}

function Workspace() {
  const fileInputRef =
    useRef<HTMLInputElement>(null);

  const [uploading, setUploading] =
    useState(false);

  const [exporting, setExporting] =
    useState(false);

  const [message, setMessage] =
    useState("");

  const [document, setDocument] =
    useState<DocumentInfo | null>(null);

  async function loadDocument(
    documentId: string,
  ) {
    const result =
      await inspectDocument(documentId);

    setDocument({
      ...result,
      fields: normalizeFields(
        result.fields ?? [],
      ),
    });
  }

  async function handleFileChange(
    event: React.ChangeEvent<HTMLInputElement>,
  ) {
    const file =
      event.target.files?.[0];

    if (!file) {
      return;
    }

    setUploading(true);
    setMessage("");
    setDocument(null);

    try {
      const result =
        await uploadDocument(file);

      await loadDocument(
        result.document_id,
      );

      setMessage(
        "Document loaded successfully.",
      );
    } catch (error) {
      console.error(error);

      setMessage(
        error instanceof Error
          ? error.message
          : "Failed to upload document.",
      );
    } finally {
      setUploading(false);

      event.target.value = "";
    }
  }

  async function refreshDocument() {
    if (!document) {
      return;
    }

    await loadDocument(
      document.document_id,
    );
  }

  async function handleExport() {
    if (!document) {
      return;
    }

    setExporting(true);
    setMessage("");

    try {
      const blob =
        await exportDocument(
          document.document_id,
        );

      const url =
        URL.createObjectURL(blob);

      const anchor =
        window.document.createElement(
          "a",
        );

      anchor.href = url;
      anchor.download =
        "smartpdf-completed.pdf";

      window.document.body.appendChild(
        anchor,
      );

      anchor.click();
      anchor.remove();

      URL.revokeObjectURL(url);

      setMessage(
        "PDF exported successfully.",
      );
    } catch (error) {
      console.error(error);

      setMessage(
        error instanceof Error
          ? error.message
          : "Failed to export PDF.",
      );
    } finally {
      setExporting(false);
    }
  }

  function openFilePicker() {
    fileInputRef.current?.click();
  }

  return (
    <main className="app-shell">
      <header className="app-header">
        <div>
          <h1>SmartPDF</h1>
          <p>
            Fill, map, sign and export PDF forms.
          </p>
        </div>

        {document && (
          <div className="header-actions">
            <button
              type="button"
              onClick={openFilePicker}
            >
              New Document
            </button>

            <button
              type="button"
              className="primary-button"
              onClick={() =>
                void handleExport()
              }
              disabled={exporting}
            >
              {exporting
                ? "Exporting..."
                : "Export PDF"}
            </button>
          </div>
        )}
      </header>

      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.png,.jpg,.jpeg,.bmp,.webp"
        onChange={handleFileChange}
        hidden
      />

      {!document && (
        <section className="upload-panel">
          <div className="upload-icon">
            PDF
          </div>

          <h2>
            Fill any PDF form
          </h2>

          <p>
            Upload a native fillable PDF,
            scanned PDF, or image form.
          </p>

          <button
            type="button"
            className="primary-button upload-button"
            onClick={openFilePicker}
            disabled={uploading}
          >
            {uploading
              ? "Processing document..."
              : "Upload Document"}
          </button>

          <small>
            Supported: PDF, PNG, JPG, JPEG,
            BMP and WEBP
          </small>
        </section>
      )}

      {document && (
        <>
          <section className="document-info">
            <div>
              <span>Document type</span>
              <strong>
                {document.form_type}
              </strong>
            </div>

            <div>
              <span>Pages</span>
              <strong>
                {document.page_count}
              </strong>
            </div>

            <div>
              <span>Fields</span>
              <strong>
                {document.fields.length}
              </strong>
            </div>

            {document.form_type ===
              "image" && (
              <div>
                <span>Mapping</span>
                <strong>
                  Manual
                </strong>
              </div>
            )}
          </section>

          {message && (
            <div className="message">
              {message}
            </div>
          )}

          <DocumentViewer
            documentId={
              document.document_id
            }
            pageCount={
              document.page_count
            }
            fields={document.fields}
            formType={document.form_type}
            onFieldsChanged={
              refreshDocument
            }
          />
        </>
      )}

      {!document && message && (
        <div className="message error-message">
          {message}
        </div>
      )}
    </main>
  );
}

export default Workspace;