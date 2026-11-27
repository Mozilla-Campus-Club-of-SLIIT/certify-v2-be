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
    assert response.headers["link"] == '</api/certificate/CERT-004>; rel="describedby"'
    mock_generate_pdf.assert_called_once_with(
        template_url="https://example.com/template.pdf",
        recipient_name="Charlie",
        name_x_pos=0.0,
        name_y_pos=0.0,
        font_size=30.0,
        font_color="#FFFFFF",
    )


@patch("routers.certificate.get_certificate_by_certificate_id")
def test_verify_certificate_valid(mock_get_cert):
    mock_get_cert.return_value = {
        "certificate_id": "CERT-100",
        "recipient_name": "Fire Fox",
        "recipient_email": "fox@example.com",
        "course_name": "Python 101",
        "event_name": "Code Night",
        "event_date": "2026-10-01",
        "issuer_name": "Mozilla Campus Club",
        "revoked": False,
        "revoked_at": None,
        "revoked_by": None,
        "revoke_reason": None,
    }

    response = client.get("/api/certificate/CERT-100")

    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["certificate"] == {
        "certificate_id": "CERT-100",
        "recipient_name": "Fire Fox",
        "course_name": "Python 101",
        "event_name": "Code Night",
        "event_date": "2026-10-01",
        "issuer_name": "Mozilla Campus Club",
        "is_valid": True,
        "revoked": False,
        "revoked_at": None,
        "revoke_reason": None,
    }


@patch("routers.certificate.get_certificate_by_certificate_id")
def test_verify_certificate_revoked(mock_get_cert):
    mock_get_cert.return_value = {
        "certificate_id": "CERT-101",
        "recipient_name": "Fire Fox",
        "revoked": True,
        "revoked_at": "2026-11-01T10:00:00+00:00",
        "revoked_by": "admin@example.com",
        "revoke_reason": "Issued by mistake",
    }

    response = client.get("/api/certificate/CERT-101")

    assert response.status_code == 200
    certificate = response.json()["certificate"]
    assert certificate["is_valid"] is False
    assert certificate["revoked"] is True
    assert certificate["revoked_at"] is not None
    assert certificate["revoke_reason"] == "Issued by mistake"
    assert "revoked_by" not in certificate
    assert "recipient_email" not in certificate


@patch("routers.certificate.get_certificate_by_certificate_id")
def test_preview_revoked_links_to_verification_endpoint(mock_get_cert):
    mock_get_cert.return_value = {
        "certificate_id": "CERT-102",
        "recipient_name": "Fire Fox",
        "revoked": True,
    }

    response = client.get("/api/certificate/CERT-102/preview")

    assert response.status_code == 410
    assert response.headers["link"] == '</api/certificate/CERT-102>; rel="describedby"'


@patch("routers.certificate.get_certificate_by_certificate_id")
def test_verify_certificate_not_found(mock_get_cert):
    mock_get_cert.side_effect = ValueError("Certificate not found")

    response = client.get("/api/certificate/MISSING")

    assert response.status_code == 404
    assert response.json()["detail"] == "Certificate not found"

