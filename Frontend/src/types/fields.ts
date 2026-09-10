export type FieldType =
  | "text"
  | "checkbox"
  | "radio"
  | "combo"
  | "list"
  | "signature"
  | "unknown";

export type NormalizedRect = {
  x: number;
  y: number;
  width: number;
  height: number;
};

export type Field = {
  id: string;
  name: string;
  field_type: FieldType;
  page_number: number;
  value: unknown;

  normalized?: NormalizedRect;

  rect?: {
    x: number;
    y: number;
    width: number;
    height: number;
  };

  signature_path?: string | null;
};