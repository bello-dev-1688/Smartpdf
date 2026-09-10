import { useState } from "react";
import type {
  CSSProperties,
  PointerEvent as ReactPointerEvent,
} from "react";

import {
  deleteImageField,
  setFieldValue,
  updateImageField,
  uploadSignature,
} from "../services/api";

import type {
  Field,
  NormalizedRect,
} from "../types/fields";

type FieldOverlayProps = {
  documentId: string;
  fields: Field[];
  pageNumber: number;
  editableMapping?: boolean;
  onFieldsChanged?: () => Promise<void> | void;
};

type DragMode = "move" | "resize";

function getNormalizedRect(
  field: Field,
): NormalizedRect | null {
  if (field.normalized) {
    return field.normalized;
  }

  const rawField = field as Field & {
    x?: number;
    y?: number;
    width?: number;
    height?: number;
  };

  if (
    typeof rawField.x === "number" &&
    typeof rawField.y === "number" &&
    typeof rawField.width === "number" &&
    typeof rawField.height === "number"
  ) {
    return {
      x: rawField.x,
      y: rawField.y,
      width: rawField.width,
      height: rawField.height,
    };
  }

  return null;
}

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

function FieldOverlay({
  documentId,
  fields,
  pageNumber,
  editableMapping = false,
  onFieldsChanged,
}: FieldOverlayProps) {
  const pageFields = fields.filter(
    (field) =>
      field.page_number === pageNumber,
  );

  const textFields = fields.filter(
    (field) =>
      field.field_type === "text",
  );

  const [values, setValues] =
    useState<Record<string, unknown>>(
      () =>
        Object.fromEntries(
          fields.map((field) => [
            field.id,
            field.value,
          ]),
        ),
    );

  const [dragging, setDragging] =
    useState<{
      fieldId: string;
      mode: DragMode;
      startX: number;
      startY: number;
      rect: NormalizedRect;
    } | null>(null);

  async function saveValue(
    fieldId: string,
    value: unknown,
  ) {
    try {
      await setFieldValue(
        documentId,
        fieldId,
        value,
      );

      setValues((current) => ({
        ...current,
        [fieldId]: value,
      }));
    } catch (error) {
      console.error(error);
    }
  }

  function moveToNextTextField(
    currentId: string,
  ) {
    const currentIndex =
      textFields.findIndex(
        (field) =>
          field.id === currentId,
      );

    if (currentIndex === -1) {
      return;
    }

    const nextField =
      textFields[currentIndex + 1];

    if (!nextField) {
      return;
    }

    const element =
      document.getElementById(
        `field-input-${nextField.id}`,
      );

    if (
      element instanceof HTMLInputElement
    ) {
      element.focus();
    }
  }

  function beginDrag(
    event: ReactPointerEvent<HTMLButtonElement>,
    field: Field,
    mode: DragMode,
  ) {
    if (!editableMapping) {
      return;
    }

    const rect =
      getNormalizedRect(field);

    if (!rect) {
      return;
    }

    event.preventDefault();
    event.stopPropagation();

    setDragging({
      fieldId: field.id,
      mode,
      startX: event.clientX,
      startY: event.clientY,
      rect,
    });

    event.currentTarget.setPointerCapture(
      event.pointerId,
    );
  }

  async function finishDrag(
    event: ReactPointerEvent<HTMLButtonElement>,
  ) {
    if (!dragging) {
      return;
    }

    event.preventDefault();
    event.stopPropagation();

    const target = fields.find(
      (field) =>
        field.id === dragging.fieldId,
    );

    if (!target) {
      setDragging(null);
      return;
    }

    const pageElement =
      document.querySelector(
        `[data-page-overlay="${pageNumber}"]`,
      );

    if (
      !(pageElement instanceof HTMLElement)
    ) {
      setDragging(null);
      return;
    }

    const bounds =
      pageElement.getBoundingClientRect();

    if (
      bounds.width <= 0 ||
      bounds.height <= 0
    ) {
      setDragging(null);
      return;
    }

    const deltaX =
      (event.clientX -
        dragging.startX) /
      bounds.width;

    const deltaY =
      (event.clientY -
        dragging.startY) /
      bounds.height;

    let nextRect: NormalizedRect;

    if (dragging.mode === "move") {
      nextRect = {
        ...dragging.rect,

        x: clamp(
          dragging.rect.x + deltaX,
          0,
          1 - dragging.rect.width,
        ),

        y: clamp(
          dragging.rect.y + deltaY,
          0,
          1 - dragging.rect.height,
        ),
      };
    } else {
      nextRect = {
        ...dragging.rect,

        width: clamp(
          dragging.rect.width + deltaX,
          0.01,
          1 - dragging.rect.x,
        ),

        height: clamp(
          dragging.rect.height + deltaY,
          0.01,
          1 - dragging.rect.y,
        ),
      };
    }

    try {
      await updateImageField(
        documentId,
        dragging.fieldId,
        nextRect,
      );

      if (onFieldsChanged) {
        await onFieldsChanged();
      }
    } catch (error) {
      console.error(error);
    } finally {
      setDragging(null);
    }
  }

  async function removeField(
    fieldId: string,
  ) {
    if (!editableMapping) {
      return;
    }

    try {
      await deleteImageField(
        documentId,
        fieldId,
      );

      if (onFieldsChanged) {
        await onFieldsChanged();
      }
    } catch (error) {
      console.error(error);
    }
  }

  async function handleSignatureUpload(
    fieldId: string,
    file: File,
  ) {
    try {
      await uploadSignature(
        documentId,
        fieldId,
        file,
      );

      if (onFieldsChanged) {
        await onFieldsChanged();
      }
    } catch (error) {
      console.error(error);
    }
  }

  function renderMappingControls(
    field: Field,
  ) {
    if (!editableMapping) {
      return null;
    }

    return (
      <div
        style={{
          position: "absolute",

          /*
           * Place the controls ABOVE
           * the field instead of inside it.
           */
          right: 0,
          bottom: "calc(100% + 5px)",

          display: "flex",
          alignItems: "center",
          gap: "4px",

          padding: "3px",

          background: "#ffffff",
          border: "1px solid #d1d5db",
          borderRadius: "6px",

          boxShadow:
            "0 2px 7px rgba(0, 0, 0, 0.18)",

          zIndex: 20,

          whiteSpace: "nowrap",
        }}
        onPointerDown={(event) =>
          event.stopPropagation()
        }
        onDoubleClick={(event) =>
          event.stopPropagation()
        }
      >
        <button
          type="button"
          title="Move field"
          aria-label={`Move ${field.name}`}
          onPointerDown={(event) =>
            beginDrag(
              event,
              field,
              "move",
            )
          }
          onPointerUp={(event) =>
            void finishDrag(event)
          }
          style={{
            width: "30px",
            height: "28px",
            padding: 0,

            border:
              "1px solid #2563eb",

            borderRadius: "4px",

            background: "#ffffff",
            color: "#2563eb",

            cursor: "move",

            fontSize: "15px",
            fontWeight: 600,
            lineHeight: 1,

            touchAction: "none",
          }}
        >
          ↔
        </button>

        <button
          type="button"
          title="Resize field"
          aria-label={`Resize ${field.name}`}
          onPointerDown={(event) =>
            beginDrag(
              event,
              field,
              "resize",
            )
          }
          onPointerUp={(event) =>
            void finishDrag(event)
          }
          style={{
            width: "30px",
            height: "28px",
            padding: 0,

            border:
              "1px solid #2563eb",

            borderRadius: "4px",

            background: "#ffffff",
            color: "#2563eb",

            cursor: "nwse-resize",

            fontSize: "15px",
            fontWeight: 600,
            lineHeight: 1,

            touchAction: "none",
          }}
        >
          ↘
        </button>

        <button
          type="button"
          title="Delete field"
          aria-label={`Delete ${field.name}`}
          onClick={() =>
            void removeField(field.id)
          }
          style={{
            width: "30px",
            height: "28px",
            padding: 0,

            border:
              "1px solid #dc2626",

            borderRadius: "4px",

            background: "#ffffff",
            color: "#dc2626",

            cursor: "pointer",

            fontSize: "18px",
            fontWeight: 600,
            lineHeight: 1,

            touchAction: "manipulation",
          }}
        >
          ×
        </button>
      </div>
    );
  }

  return (
    <>
      {pageFields.map((field) => {
        const rect =
          getNormalizedRect(field);

        if (!rect) {
          return null;
        }

        const commonStyle: CSSProperties = {
          position: "absolute",

          left: `${rect.x * 100}%`,
          top: `${rect.y * 100}%`,

          width: `${rect.width * 100}%`,
          height: `${rect.height * 100}%`,

          boxSizing: "border-box",
        };

        /*
         * Native text field
         */
        if (
          field.field_type === "text" &&
          !editableMapping
        ) {
          return (
            <input
              key={field.id}
              id={`field-input-${field.id}`}
              type="text"
              value={String(
                values[field.id] ?? "",
              )}
              onChange={(event) => {
                setValues((current) => ({
                  ...current,
                  [field.id]:
                    event.target.value,
                }));
              }}
              onBlur={(event) => {
                void saveValue(
                  field.id,
                  event.target.value,
                );
              }}
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  event.preventDefault();

                  void saveValue(
                    field.id,
                    event.currentTarget.value,
                  );

                  moveToNextTextField(
                    field.id,
                  );
                }
              }}
              aria-label={field.name}
              style={{
                ...commonStyle,

                border:
                  "2px solid #2563eb",

                borderRadius: "3px",

                background:
                  "rgba(255, 255, 255, 0.85)",

                padding: "2px 6px",

                fontSize: "14px",

                outline: "none",

                zIndex: 3,
              }}
            />
          );
        }

        /*
         * Native checkbox
         */
        if (
          field.field_type ===
            "checkbox" &&
          !editableMapping
        ) {
          return (
            <input
              key={field.id}
              id={`field-input-${field.id}`}
              type="checkbox"
              checked={Boolean(
                values[field.id],
              )}
              onChange={(event) => {
                void saveValue(
                  field.id,
                  event.target.checked,
                );
              }}
              aria-label={field.name}
              style={{
                ...commonStyle,

                margin: 0,

                cursor: "pointer",

                accentColor:
                  "#2563eb",

                zIndex: 3,
              }}
            />
          );
        }

        /*
         * Native signature field
         */
        if (
          field.field_type ===
            "signature" &&
          !editableMapping
        ) {
          return (
            <div
              key={field.id}
              style={{
                ...commonStyle,

                border:
                  "2px dashed #7c3aed",

                borderRadius: "4px",

                background:
                  "rgba(124, 58, 237, 0.08)",

                display: "flex",
                alignItems: "center",
                justifyContent:
                  "center",

                zIndex: 3,
              }}
            >
              <label
                style={{
                  cursor: "pointer",

                  fontSize: "13px",

                  fontWeight: 600,

                  color: "#7c3aed",

                  background: "white",

                  border:
                    "1px solid #7c3aed",

                  borderRadius: "6px",

                  padding: "7px 12px",

                  userSelect: "none",
                }}
              >
                Upload Signature

                <input
                  type="file"
                  accept="image/png,image/jpeg,image/webp"
                  style={{
                    display: "none",
                  }}
                  onChange={(event) => {
                    const file =
                      event.target.files?.[0];

                    if (file) {
                      void handleSignatureUpload(
                        field.id,
                        file,
                      );
                    }

                    event.target.value = "";
                  }}
                />
              </label>
            </div>
          );
        }

        /*
         * Scanned/image-form mapping mode
         */
        if (
          editableMapping &&
          (
            field.field_type ===
              "text" ||
            field.field_type ===
              "checkbox" ||
            field.field_type ===
              "signature"
          )
        ) {
          const border =
            field.field_type ===
            "text"
              ? "#2563eb"
              : field.field_type ===
                  "checkbox"
                ? "#16a34a"
                : "#7c3aed";

          const background =
            field.field_type ===
            "text"
              ? "rgba(37, 99, 235, 0.10)"
              : field.field_type ===
                  "checkbox"
                ? "rgba(22, 163, 74, 0.10)"
                : "rgba(124, 58, 237, 0.10)";

          return (
            <div
              key={field.id}
              style={{
                ...commonStyle,

                border:
                  `2px solid ${border}`,

                background,

                borderRadius: "4px",

                zIndex: 4,

                touchAction: "none",
              }}
            >
              <div
                style={{
                  width: "100%",
                  height: "100%",

                  display: "flex",

                  alignItems:
                    "center",

                  justifyContent:
                    "center",

                  fontSize: "11px",

                  fontWeight: 600,

                  color: border,

                  pointerEvents:
                    "none",

                  userSelect: "none",
                }}
              >
                {field.field_type.toUpperCase()}
              </div>

              {renderMappingControls(
                field,
              )}
            </div>
          );
        }

        /*
         * Signature upload for mapped
         * image field.
         */
        if (
          field.field_type ===
            "signature" &&
          !editableMapping
        ) {
          return (
            <div
              key={field.id}
              style={{
                ...commonStyle,

                border:
                  "2px dashed #7c3aed",

                background:
                  "rgba(124, 58, 237, 0.08)",

                display: "flex",

                alignItems:
                  "center",

                justifyContent:
                  "center",

                zIndex: 3,
              }}
            >
              <label
                style={{
                  cursor: "pointer",

                  fontSize: "12px",

                  color: "#7c3aed",

                  textAlign: "center",

                  padding: "4px",
                }}
              >
                Upload signature

                <input
                  type="file"
                  accept="image/png,image/jpeg,image/webp"
                  style={{
                    display: "none",
                  }}
                  onChange={(event) => {
                    const file =
                      event.target.files?.[0];

                    if (file) {
                      void handleSignatureUpload(
                        field.id,
                        file,
                      );
                    }

                    event.target.value = "";
                  }}
                />
              </label>
            </div>
          );
        }

        return null;
      })}
    </>
  );
}

export default FieldOverlay;