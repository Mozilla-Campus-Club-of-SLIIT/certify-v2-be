from fastapi import APIRouter, HTTPException, Response

from models.models import CertificateVerificationResponseModel
from services.certificate_pdf import generate_certificate_pdf_bytes
from services.database import get_certificate_by_certificate_id, get_template_by_id

router = APIRouter(
    prefix="/certificate",
    tags=["certificate"],
)


@router.get(
    "/{certificate_id}",
    response_model=CertificateVerificationResponseModel,
    responses={
        404: {"description": "Certificate not found"},
    },
)
def verify_certificate(certificate_id: str):
    try:
        certificate = get_certificate_by_certificate_id(certificate_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    revoked = bool(certificate.get("revoked"))

    return {
        "ok": True,
        "certificate": {
            "certificate_id": certificate.get("certificate_id") or certificate_id,
            "recipient_name": certificate.get("recipient_name"),
            "course_name": certificate.get("course_name"),
            "event_name": certificate.get("event_name"),
            "event_date": certificate.get("event_date"),
            "issuer_name": certificate.get("issuer_name"),
            "is_valid": not revoked,
            "revoked": revoked,
            "revoked_at": certificate.get("revoked_at"),
            "revoke_reason": certificate.get("revoke_reason"),
        },
    }


@router.get(
    "/{certificate_id}/preview",
    responses={
        400: {"description": "Certificate preview generation failed"},
        404: {"description": "Certificate not found"},
        410: {"description": "Certificate has been revoked"},
    },
)
def preview_certificate(certificate_id: str):
    try:
        certificate = get_certificate_by_certificate_id(certificate_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    link_header = f'</api/certificate/{certificate_id}>; rel="describedby"'

    if certificate.get("revoked"):
        raise HTTPException(
            status_code=410,
            detail="Certificate has been revoked",
            headers={"Link": link_header},
        )

    try:
        template = get_template_by_id(certificate["template_id"])

        if not template.get("url"):
            raise ValueError("Template URL is missing")

        name_x_pos = float(template["name_x_pos"]) if template.get("name_x_pos") is not None else 720.0
        name_y_pos = float(template["name_y_pos"]) if template.get("name_y_pos") is not None else 360.0
        font_size = float(template["font_size"]) if template.get("font_size") is not None else 55.0

        pdf_bytes = generate_certificate_pdf_bytes(
            template_url=template["url"],
            recipient_name=certificate["recipient_name"],
            name_x_pos=name_x_pos,
            name_y_pos=name_y_pos,
            font_size=font_size,
            font_color=template.get("font_color"),
        )

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'inline; filename="certificate-{certificate_id}.pdf"',
                "Link": link_header,
            },
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
