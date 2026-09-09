from typing import Any, Literal

from pydantic import BaseModel, Field


class ImageFieldCreate(BaseModel):
    id: str = Field(min_length=1)
    page_number: int = Field(ge=0)
    field_type: Literal["text", "checkbox", "signature"]
    x: float = Field(ge=0, le=1)
    y: float = Field(ge=0, le=1)
    width: float = Field(gt=0, le=1)
    height: float = Field(gt=0, le=1)
    name: str | None = None


class ImageFieldUpdate(BaseModel):
    name: str | None = None
    page_number: int | None = Field(default=None, ge=0)
    field_type: Literal["text", "checkbox", "signature"] | None = None
    x: float | None = Field(default=None, ge=0, le=1)
    y: float | None = Field(default=None, ge=0, le=1)
    width: float | None = Field(default=None, gt=0, le=1)
    height: float | None = Field(default=None, gt=0, le=1)


class FieldValueUpdate(BaseModel):
    value: Any
