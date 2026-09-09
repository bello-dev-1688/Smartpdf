from pathlib import Path

import pymupdf
import pytest

from pdf_form_filler.services.document_service import DocumentService


ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "sample.pdf"


def make_service(tmp_path):
    return DocumentService(tmp_path / "documents")


def test_image_field_mapping_create_update_delete(tmp_path):
    service = make_service(tmp_path)
    document_id = service.upload(SAMPLE)

    field = service.add_image_field(
        document_id,
        field_id="mobile_name",
        page_number=0,
        field_type="text",
        x=0.10,
        y=0.20,
        width=0.70,
        height=0.04,
    )
    assert field["field_type"] == "text"
    assert field["x"] == 0.10

    updated = service.update_image_field(
        document_id, "mobile_name", x=0.12, width=0.65
    )
    assert updated["x"] == 0.12
    assert updated["width"] == 0.65

    assert any(f["id"] == "mobile_name" for f in service.list_fields(document_id))
    assert service.delete_image_field(document_id, "mobile_name")["status"] == "deleted"
    assert not any(f["id"] == "mobile_name" for f in service.list_fields(document_id))


def test_image_field_value_exports_and_source_is_untouched(tmp_path):
    service = make_service(tmp_path)
    document_id = service.upload(SAMPLE)
    directory = tmp_path / "documents" / document_id
    original_source = (directory / "source.pdf").read_bytes()

    service.add_image_field(
        document_id, "name", 0, "text", 0.10, 0.20, 0.70, 0.04
    )
    service.set_field_value(document_id, "name", "Backend test")

    output = tmp_path / "filled.pdf"
    service.export(document_id, output)

    assert output.exists()
    assert (directory / "source.pdf").read_bytes() == original_source

    exported = pymupdf.open(output)
    try:
        text = "".join(page.get_text() for page in exported)
        assert "Backend test" in text
    finally:
        exported.close()


def test_repeated_exports_do_not_duplicate_image_overlay(tmp_path):
    service = make_service(tmp_path)
    document_id = service.upload(SAMPLE)
    service.add_image_field(
        document_id, "name", 0, "text", 0.10, 0.20, 0.70, 0.04
    )
    service.set_field_value(document_id, "name", "Once")

    output1 = tmp_path / "one.pdf"
    output2 = tmp_path / "two.pdf"
    service.export(document_id, output1)
    service.export(document_id, output2)

    texts = []
    for path in (output1, output2):
        document = pymupdf.open(path)
        try:
            texts.append("".join(page.get_text() for page in document))
        finally:
            document.close()

    assert texts[0].count("Once") == 1
    assert texts[1].count("Once") == 1


def test_invalid_mapping_is_rejected(tmp_path):
    service = make_service(tmp_path)
    document_id = service.upload(SAMPLE)

    with pytest.raises(ValueError):
        service.add_image_field(
            document_id, "bad", 0, "text", 0.9, 0.9, 0.2, 0.2
        )
