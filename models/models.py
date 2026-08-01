from fastapi import UploadFile
from pydantic import BaseModel, Field


class AddTemplateRequestModel(BaseModel):
	font_size: str
	font_color: str = Field(pattern=r'^#(?:[0-9a-fA-F]{3}){1,2}$')
	name_x_pos: int
	name_y_pos: int
	template_name: str | None = None
	template_for: str | None = None
	event_name: str | None = None
	issuer_name: str | None = None
	notes: str | None = None


class AddCertificateRequestModel(BaseModel):
	certificate_id: str | None = None
	template_id: int
	recipient_name: str
	recipient_email: str
	issue_reason: str | None = None
	event_name: str | None = None
	event_date: str | None = None
	event_location: str | None = None
	issuer_name: str | None = None
	course_name: str | None = None
	notes: str | None = None
