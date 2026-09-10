import {
  useEffect,
  useState,
} from "react";

import {
  createImageField,
  renderPage,
} from "../services/api";

import FieldOverlay from "./FieldOverlay";

import type {
  Field,
  NormalizedRect,
} from "../types/fields";

type DocumentViewerProps = {
  documentId: string;
  pageCount: number;
  fields: Field[];
  formType: string;
  onFieldsChanged: () => Promise<void> | void;
};

type ImageFieldType =
  | "text"
  | "checkbox"
  | "signature";

type PendingField = {
  pageNumber: number;
  rect: NormalizedRect;
};

const SIZE_STEP = 0.01;

function clamp(
  value: number,
  min: number,
  max: number,
) {
  return Math.min(
    Math.max(value, min),
    max,
  );
}

function getDefaultSize(
  type: ImageFieldType,
) {
  switch (type) {
    case "checkbox":
      return {
        width: 0.035,
        height: 0.035,
      };

    case "signature":
      return {
        width: 0.20,
        height: 0.055,
      };

    case "text":
    default:
      return {
        width: 0.16,
        height: 0.035,
      };
  }
}

function createCenteredRect(
  centerX: number,
  centerY: number,
  width: number,
  height: number,
): NormalizedRect {
  const x = clamp(
    centerX - width / 2,
    0,
    1 - width,
  );

  const y = clamp(
    centerY - height / 2,
    0,
    1 - height,
  );

  return {
    x,
    y,
    width,
    height,
  };
}

function DocumentViewer({
  documentId,
  pageCount,
  fields,
  formType,
  onFieldsChanged,
}: DocumentViewerProps) {
  const [pageUrls, setPageUrls] =
    useState<string[]>([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  const [mappingMode, setMappingMode] =
    useState(formType === "image");

  const [pendingField, setPendingField] =
    useState<PendingField | null>(null);

  const [fieldName, setFieldName] =
    useState("");

  const [fieldType, setFieldType] =
    useState<ImageFieldType>("text");

  const [creating, setCreating] =
    useState(false);

  const [zoom, setZoom] =
    useState(1);

  useEffect(() => {
    let cancelled = false;

    const objectUrls: string[] = [];

    async function loadPages() {
      setLoading(true);
      setError("");

      try {
        const urls: string[] = [];

        for (
          let page = 0;
          page < pageCount;
          page++
        ) {
          const blob = await renderPage(
            documentId,
            page,
            zoom,
          );

          const url =
            URL.createObjectURL(blob);

          objectUrls.push(url);
          urls.push(url);
        }

        if (!cancelled) {
          setPageUrls(urls);
        }
      } catch (err) {
        console.error(err);

        if (!cancelled) {
          setError(
            "Failed to render document.",
          );
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void loadPages();

    return () => {
      cancelled = true;

      for (const url of objectUrls) {
        URL.revokeObjectURL(url);
      }
    };
  }, [
    documentId,
    pageCount,
    zoom,
  ]);

  function handleDoubleClick(
    event: React.MouseEvent<HTMLDivElement>,
    pageNumber: number,
  ) {
    if (!mappingMode) {
      return;
    }

    const target =
      event.target as HTMLElement;

    if (
      target.closest(
        "input, button, select, textarea, label",
      )
    ) {
      return;
    }

    const rect =
      event.currentTarget.getBoundingClientRect();

    const pointX =
      (event.clientX - rect.left) /
      rect.width;

    const pointY =
      (event.clientY - rect.top) /
      rect.height;

    const size =
      getDefaultSize(fieldType);

    setPendingField({
      pageNumber,
      rect: createCenteredRect(
        pointX,
        pointY,
        size.width,
        size.height,
      ),
    });

    setFieldName("");
  }

  function changeFieldType(
    type: ImageFieldType,
  ) {
    setFieldType(type);

    if (!pendingField) {
      return;
    }

    const centerX =
      pendingField.rect.x +
      pendingField.rect.width / 2;

    const centerY =
      pendingField.rect.y +
      pendingField.rect.height / 2;

    const size =
      getDefaultSize(type);

    setPendingField({
      ...pendingField,
      rect: createCenteredRect(
        centerX,
        centerY,
        size.width,
        size.height,
      ),
    });
  }

  function changeWidth(
    direction: "increase" | "decrease",
  ) {
    if (!pendingField) {
      return;
    }

    const current =
      pendingField.rect;

    const newWidth =
      direction === "increase"
        ? current.width + SIZE_STEP
        : current.width - SIZE_STEP;

    const width = clamp(
      newWidth,
      0.025,
      0.95,
    );

    const centerX =
      current.x +
      current.width / 2;

    const centerY =
      current.y +
      current.height / 2;

    setPendingField({
      ...pendingField,
      rect: createCenteredRect(
        centerX,
        centerY,
        width,
        current.height,
      ),
    });
  }

  function changeHeight(
    direction: "increase" | "decrease",
  ) {
    if (!pendingField) {
      return;
    }

    const current =
      pendingField.rect;

    const newHeight =
      direction === "increase"
        ? current.height + SIZE_STEP
        : current.height - SIZE_STEP;

    const height = clamp(
      newHeight,
      0.02,
      0.50,
    );

    const centerX =
      current.x +
      current.width / 2;

    const centerY =
      current.y +
      current.height / 2;

    setPendingField({
      ...pendingField,
      rect: createCenteredRect(
        centerX,
        centerY,
        current.width,
        height,
      ),
    });
  }

  async function confirmField() {
    if (!pendingField) {
      return;
    }

    setCreating(true);

    try {
      const id =
        fieldName.trim() ||
        `${fieldType}_${Date.now()}`;

      await createImageField(
        documentId,
        {
          id,
          page_number:
            pendingField.pageNumber,
          field_type: fieldType,
          x: pendingField.rect.x,
          y: pendingField.rect.y,
          width:
            pendingField.rect.width,
          height:
            pendingField.rect.height,
          name:
            fieldName.trim() ||
            undefined,
        },
      );

      setPendingField(null);

      await onFieldsChanged();
    } catch (err) {
      console.error(err);

      window.alert(
        err instanceof Error
          ? err.message
          : "Failed to create field.",
      );
    } finally {
      setCreating(false);
    }
  }

  if (loading) {
    return (
      <div className="viewer-status">
        Rendering document...
      </div>
    );
  }

  if (error) {
    return (
      <div className="viewer-status viewer-error">
        {error}
      </div>
    );
  }

  return (
    <div className="document-viewer">
      <div className="viewer-toolbar">
        <div className="toolbar-group">
          <button
            type="button"
            onClick={() =>
              setZoom((value) =>
                Math.max(
                  0.5,
                  Number(
                    (
                      value - 0.1
                    ).toFixed(1),
                  ),
                ),
              )
            }
          >
            −
          </button>

          <span>
            {Math.round(
              zoom * 100,
            )}
            %
          </span>

          <button
            type="button"
            onClick={() =>
              setZoom((value) =>
                Math.min(
                  2,
                  Number(
                    (
                      value + 0.1
                    ).toFixed(1),
                  ),
                ),
              )
            }
          >
            +
          </button>
        </div>

        {formType === "image" && (
          <button
            type="button"
            className={
              mappingMode
                ? "toolbar-button active"
                : "toolbar-button"
            }
            onClick={() =>
              setMappingMode(
                (current) => !current,
              )
            }
          >
            {mappingMode
              ? "Mapping Mode: ON"
              : "Edit Mapping"}
          </button>
        )}

        {mappingMode &&
          formType === "image" && (
            <span className="mapping-hint">
              Double-click or double-tap
              the document to add a field.
            </span>
          )}
      </div>

      <div className="pages">
        {pageUrls.map(
          (url, index) => (
            <div
              key={url}
              className="page-section"
            >
              <div className="page-label">
                Page {index + 1}
              </div>

              <div
                className="page-canvas"
                data-page-overlay={index}
                onDoubleClick={(event) =>
                  handleDoubleClick(
                    event,
                    index,
                  )
                }
                style={{
                  touchAction:
                    "manipulation",
                }}
              >
                <img
                  src={url}
                  alt={`Page ${
                    index + 1
                  }`}
                  draggable={false}
                />

                <FieldOverlay
                  documentId={documentId}
                  fields={fields}
                  pageNumber={index}
                  editableMapping={
                    mappingMode &&
                    formType === "image"
                  }
                  onFieldsChanged={
                    onFieldsChanged
                  }
                />
              </div>
            </div>
          ),
        )}
      </div>

      {pendingField && (
        <div
          className="modal-backdrop"
          onClick={() =>
            setPendingField(null)
          }
        >
          <div
            className="field-modal"
            onClick={(event) =>
              event.stopPropagation()
            }
          >
            <h3>
              Add Form Field
            </h3>

            <label>
              Field type

              <select
                value={fieldType}
                onChange={(event) =>
                  changeFieldType(
                    event.target
                      .value as ImageFieldType,
                  )
                }
              >
                <option value="text">
                  Text
                </option>

                <option value="checkbox">
                  Checkbox
                </option>

                <option value="signature">
                  Signature
                </option>
              </select>
            </label>

            <label>
              Field name

              <input
                value={fieldName}
                onChange={(event) =>
                  setFieldName(
                    event.target.value,
                  )
                }
                placeholder="Optional field name"
              />
            </label>

            <div className="field-size-controls">
              <div className="size-control">
                <span>
                  Width
                </span>

                <div className="size-buttons">
                  <button
                    type="button"
                    onClick={() =>
                      changeWidth(
                        "decrease",
                      )
                    }
                    aria-label="Decrease field width"
                  >
                    −
                  </button>

                  <button
                    type="button"
                    onClick={() =>
                      changeWidth(
                        "increase",
                      )
                    }
                    aria-label="Increase field width"
                  >
                    +
                  </button>
                </div>
              </div>

              <div className="size-control">
                <span>
                  Height
                </span>

                <div className="size-buttons">
                  <button
                    type="button"
                    onClick={() =>
                      changeHeight(
                        "decrease",
                      )
                    }
                    aria-label="Decrease field height"
                  >
                    −
                  </button>

                  <button
                    type="button"
                    onClick={() =>
                      changeHeight(
                        "increase",
                      )
                    }
                    aria-label="Increase field height"
                  >
                    +
                  </button>
                </div>
              </div>
            </div>

            <div className="size-preview">
              Adjust the field size using
              the buttons. The field stays
              centered on its original
              position.
            </div>

            <div className="modal-actions">
              <button
                type="button"
                onClick={() =>
                  setPendingField(null)
                }
                disabled={creating}
              >
                Cancel
              </button>

              <button
                type="button"
                className="primary-button"
                onClick={() =>
                  void confirmField()
                }
                disabled={creating}
              >
                {creating
                  ? "Creating..."
                  : "Confirm Field"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default DocumentViewer;