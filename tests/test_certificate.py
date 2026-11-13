from unittest.mock import patch
from fastapi.testclient import TestClient

from main import app
from routers.certificate import preview_certificate


client = TestClient(app)


@patch("routers.certificate.generate_certificate_pdf_bytes")
@patch("routers.certificate.get_template_by_id")
@patch("routers.certificate.get_certificate_by_certificate_id")
def test_preview_certificate_respects_zero_coordinates(
    mock_get_cert, mock_get_template, mock_generate_pdf
):
    mock_get_cert.return_value = {
        "certificate_id": "CERT-001",
        "recipient_name": "John Doe",
        "template_id": "tpl-1",
        "revoked": False,
    }
    mock_get_template.return_value = {
        "url": "https://example.com/template.pdf",
        "name_x_pos": 0,
        "name_y_pos": 0,
        "font_size": 0,
        "font_color": "#000000",
    }
    mock_generate_pdf.return_value = b"%PDF-mock-content"

    response = preview_certificate("CERT-001")

    assert response.status_code == 200
    mock_generate_pdf.assert_called_once_with(
        template_url="https://example.com/template.pdf",
        recipient_name="John Doe",
        name_x_pos=0.0,
        name_y_pos=0.0,
        font_size=0.0,
        font_color="#000000",
    )


@patch("routers.certificate.generate_certificate_pdf_bytes")
@patch("routers.certificate.get_template_by_id")
@patch("routers.certificate.get_certificate_by_certificate_id")
def test_preview_certificate_fallback_when_none(
    mock_get_cert, mock_get_template, mock_generate_pdf
):
    mock_get_cert.return_value = {
        "certificate_id": "CERT-002",
        "recipient_name": "Jane Doe",
        "template_id": "tpl-2",
        "revoked": False,
    }
    mock_get_template.return_value = {
        "url": "https://example.com/template.pdf",
        "name_x_pos": None,
        "name_y_pos": None,
        "font_size": None,
        "font_color": None,
    }
    mock_generate_pdf.return_value = b"%PDF-mock-content"

    response = preview_certificate("CERT-002")

    assert response.status_code == 200
    mock_generate_pdf.assert_called_once_with(
        template_url="https://example.com/template.pdf",
        recipient_name="Jane Doe",
        name_x_pos=720.0,
        name_y_pos=360.0,
        font_size=55.0,
        font_color=None,
    )


@patch("routers.certificate.generate_certificate_pdf_bytes")
@patch("routers.certificate.get_template_by_id")
@patch("routers.certificate.get_certificate_by_certificate_id")
def test_preview_certificate_fallback_when_keys_missing(
    mock_get_cert, mock_get_template, mock_generate_pdf
):
    mock_get_cert.return_value = {
        "certificate_id": "CERT-003",
        "recipient_name": "Bob Smith",
        "template_id": "tpl-3",
        "revoked": False,
    }
    mock_get_template.return_value = {
        "url": "https://example.com/template.pdf",
    }
    mock_generate_pdf.return_value = b"%PDF-mock-content"

    response = preview_certificate("CERT-003")

    assert response.status_code == 200
    mock_generate_pdf.assert_called_once_with(
        template_url="https://example.com/template.pdf",
        recipient_name="Bob Smith",
        name_x_pos=720.0,
        name_y_pos=360.0,
        font_size=55.0,
        font_color=None,
    )


@patch("routers.certificate.generate_certificate_pdf_bytes")
@patch("routers.certificate.get_template_by_id")
@patch("routers.certificate.get_certificate_by_certificate_id")
def test_preview_certificate_via_testclient_respects_zero(
    mock_get_cert, mock_get_template, mock_generate_pdf
):
    mock_get_cert.return_value = {
        "certificate_id": "CERT-004",
        "recipient_name": "Charlie",
        "template_id": "tpl-4",
        "revoked": False,
    }
    mock_get_template.return_value = {
        "url": "https://example.com/template.pdf",
        "name_x_pos": 0,
        "name_y_pos": 0,
        "font_size": 30,
        "font_color": "#FFFFFF",
    }
    mock_generate_pdf.return_value = b"%PDF-mock-content"

    response = client.get("/api/certificate/CERT-004/preview")

    assert response.status_code == 200
    assert response.content == b"%PDF-mock-content"
    assert response.headers["content-type"] == "application/pdf"
    assert 'filename="certificate-CERT-004.pdf"' in response.headers["content-disposition"]
    mock_generate_pdf.assert_called_once_with(
        template_url="https://example.com/template.pdf",
        recipient_name="Charlie",
        name_x_pos=0.0,
        name_y_pos=0.0,
        font_size=30.0,
        font_color="#FFFFFF",
    )

