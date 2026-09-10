const API_BASE_URL = "http://127.0.0.1:8000";

async function parseError(response: Response) {
  try {
    const data = await response.json();

    if (typeof data?.detail === "string") {
      return data.detail;
    }

    return `Request failed: ${response.status}`;
  } catch {
    return `Request failed: ${response.status}`;
  }
}

export async function uploadDocument(file: File) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/documents`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error(await parseError(response));
  }

  return response.json();
}

export async function inspectDocument(documentId: string) {
  const response = await fetch(
    `${API_BASE_URL}/documents/${documentId}`,
  );

  if (!response.ok) {
    throw new Error(await parseError(response));
  }

  return response.json();
}

export async function renderPage(
  documentId: string,
  pageNumber: number,
  zoom = 1,
) {
  const response = await fetch(
    `${API_BASE_URL}/documents/${documentId}/pages/${pageNumber}/render?zoom=${zoom}`,
  );

  if (!response.ok) {
    throw new Error(await parseError(response));
  }

  return response.blob();
}

export async function setFieldValue(
  documentId: string,
  fieldId: string,
  value: unknown,
) {
  const response = await fetch(
    `${API_BASE_URL}/documents/${documentId}/fields/${encodeURIComponent(fieldId)}`,
    {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ value }),
    },
  );

  if (!response.ok) {
    throw new Error(await parseError(response));
  }

  return response.json();
}

export async function createImageField(
  documentId: string,
  field: {
    id: string;
    page_number: number;
    field_type: "text" | "checkbox" | "signature";
    x: number;
    y: number;
    width: number;
    height: number;
    name?: string;
  },
) {
  const response = await fetch(
    `${API_BASE_URL}/documents/${documentId}/fields`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(field),
    },
  );

  if (!response.ok) {
    throw new Error(await parseError(response));
  }

  return response.json();
}

export async function updateImageField(
  documentId: string,
  fieldId: string,
  changes: Partial<{
    name: string;
    page_number: number;
    field_type: "text" | "checkbox" | "signature";
    x: number;
    y: number;
    width: number;
    height: number;
  }>,
) {
  const response = await fetch(
    `${API_BASE_URL}/documents/${documentId}/fields/${encodeURIComponent(fieldId)}`,
    {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(changes),
    },
  );

  if (!response.ok) {
    throw new Error(await parseError(response));
  }

  return response.json();
}

export async function deleteImageField(
  documentId: string,
  fieldId: string,
) {
  const response = await fetch(
    `${API_BASE_URL}/documents/${documentId}/fields/${encodeURIComponent(fieldId)}`,
    {
      method: "DELETE",
    },
  );

  if (!response.ok) {
    throw new Error(await parseError(response));
  }

  return response.json();
}

export async function uploadSignature(
  documentId: string,
  fieldId: string,
  file: File,
) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(
    `${API_BASE_URL}/documents/${documentId}/fields/${encodeURIComponent(fieldId)}/signature`,
    {
      method: "POST",
      body: formData,
    },
  );

  if (!response.ok) {
    throw new Error(await parseError(response));
  }

  return response.json();
}

export async function exportDocument(documentId: string) {
  const response = await fetch(
    `${API_BASE_URL}/documents/${documentId}/export`,
    {
      method: "POST",
    },
  );

  if (!response.ok) {
    throw new Error(await parseError(response));
  }

  return response.blob();
}