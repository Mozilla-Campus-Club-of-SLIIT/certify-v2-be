from unittest.mock import patch
from fastapi.testclient import TestClient

from main import app
from utils.auth import verify_admin

app.dependency_overrides[verify_admin] = lambda: {"email": "admin@test.com"}
client = TestClient(app)

FORM = {
    "font_size": "24",
    "font_color": "#000000",
    "name_x_pos": "100",
    "name_y_pos": "200",
}


def test_png_template_rejected():
    files = {"template": ("t.png", b"\x89PNG fake", "image/png")}
    response = client.post("/api/admin/add/template", data=FORM, files=files)
    assert response.status_code == 422


def test_jpeg_template_rejected():
    files = {"template": ("t.jpg", b"\xff\xd8 fake", "image/jpeg")}
    response = client.post("/api/admin/add/template", data=FORM, files=files)
    assert response.status_code == 422


@patch("routers.admin.add_template")
@patch("routers.admin.upload_template")
def test_pdf_template_accepted(mock_upload, mock_add):
    mock_upload.return_value = {"file_path": "x.pdf", "public_url": "https://example.com/x.pdf", "filename": "t.pdf"}
    mock_add.return_value = {"id": 1}
    files = {"template": ("t.pdf", b"%PDF-1.4 fake", "application/pdf")}
    response = client.post("/api/admin/add/template", data=FORM, files=files)
    assert response.status_code == 200
