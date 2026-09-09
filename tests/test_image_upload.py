from pathlib import Path

from fastapi.testclient import TestClient
from PIL import Image, ImageDraw

from pdf_form_filler.api.app import app
from pdf_form_filler.api.dependencies import service


client = TestClient(app)


def test_png_upload_becomes_image_document(tmp_path):
    image_path = tmp_path / "form.png"

    image = Image.new("RGB", (1200, 1600), "white")
    draw = ImageDraw.Draw(image)
    draw.rectangle((100, 200, 1100, 300), outline="black", width=4)
    draw.text((120, 225), "Name of individual", fill="black")
    image.save(image_path)

    with image_path.open("rb") as file:
        response = client.post(
            "/documents",
            files={
                "file": (
                    "form.png",
                    file,
                    "image/png",
                )
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["document_id"]
    assert data["form_type"] == "image"
    assert data["page_count"] == 1
    assert data["fields"] == []

    document_id = data["document_id"]

    source = service.storage.source(document_id)
    working = service.storage.working(document_id)

    assert source.exists()
    assert working.exists()


def test_jpeg_upload_can_be_mapped_and_exported(tmp_path):
    image_path = tmp_path / "form.jpg"

    image = Image.new("RGB", (1000, 1400), "white")
    image.save(image_path, quality=95)

    with image_path.open("rb") as file:
        response = client.post(
            "/documents",
            files={
                "file": (
                    "form.jpg",
                    file,
                    "image/jpeg",
                )
            },
        )

    assert response.status_code == 200

    document_id = response.json()["document_id"]

    response = client.post(
        f"/documents/{document_id}/fields",
        json={
            "id": "name",
            "page_number": 0,
            "field_type": "text",
            "x": 0.10,
            "y": 0.20,
            "width": 0.70,
            "height": 0.04,
        },
    )
    print("Status code:", response.status_code)
    print("Response content:", response.content)
    print("Response:", response.text)
    assert response.status_code == 200

    response = client.put(
        f"/documents/{document_id}/fields/name",
        json={"value": "Bello Basit"},
    )

    assert response.status_code == 200

    output = tmp_path / "filled.pdf"
    service.export(document_id, output)

    assert output.exists()
    assert output.stat().st_size > 0

    source_bytes = service.storage.source(document_id).read_bytes()
    assert source_bytes != output.read_bytes()
