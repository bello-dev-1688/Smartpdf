from dataclasses import dataclass
from enum import Enum
from typing import Any

class FormType(str, Enum):
    NATIVE = "native"
    IMAGE = "image"

class FieldType(str, Enum):
    TEXT = "text"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    COMBO = "combo"
    LIST = "list"
    SIGNATURE = "signature"
    UNKNOWN = "unknown"

@dataclass
class Field:
    id: str
    name: str
    field_type: FieldType
    page_number: int
    rect: Any
    value: Any = None
    widget: Any = None
    normalized: bool = False

    @property
    def is_text(self): return self.field_type == FieldType.TEXT
    @property
    def is_checkbox(self): return self.field_type == FieldType.CHECKBOX
    @property
    def is_signature(self): return self.field_type == FieldType.SIGNATURE
