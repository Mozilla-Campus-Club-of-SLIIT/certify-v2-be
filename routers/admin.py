from typing import Annotated
from fastapi import APIRouter, Depends, File, Form, UploadFile
from models.models import AddCertificateRequestModel, AddTemplateRequestModel
from services.database import add_certificate, add_template
from services.storage import upload_template
from utils.auth import verify_admin

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(verify_admin)],
)


@router.post("/add/template")
async def admin_add_template(
    template: Annotated[UploadFile, File(...)],
    font_size: Annotated[str, Form(...)],
    font_color: Annotated[str, Form(...)],
    name_x_pos: Annotated[int, Form(...)],
    name_y_pos: Annotated[int, Form(...)],
    template_name: Annotated[str | None, Form()] = None,
    template_for: Annotated[str | None, Form()] = None,
    event_name: Annotated[str | None, Form()] = None,
    issuer_name: Annotated[str | None, Form()] = None,
    notes: Annotated[str | None, Form()] = None,
):
    request_data = AddTemplateRequestModel(
        font_size=font_size,
        font_color=font_color,
        name_x_pos=name_x_pos,
        name_y_pos=name_y_pos,
        template_name=template_name,
        template_for=template_for,
        event_name=event_name,
        issuer_name=issuer_name,
        notes=notes,
    )
    upload_result = await upload_template(template)
    db_record = add_template(upload_result["public_url"], request_data)

    return {
        "ok": True,
        "message": "Template added successfully",
        "upload": upload_result,
        "template": db_record,
        "data": request_data.model_dump(),
    }


@router.post("/add/certificate")
def admin_add_certificate(request: AddCertificateRequestModel):
    certificate = add_certificate(request)

    return {
        "ok": True,
        "message": "Certificate added successfully",
        "certificate": certificate,
    }

