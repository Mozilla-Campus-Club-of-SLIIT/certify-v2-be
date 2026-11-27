from fastapi import UploadFile
from pydantic import BaseModel, Field
from datetime import datetime


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


class RevokeCertificateRequestModel(BaseModel):
	revoked: bool
	reason: str | None = None


class CertificateVerificationModel(BaseModel):
	certificate_id: str
	recipient_name: str
	course_name: str | None = None
	event_name: str | None = None
	event_date: str | None = None
	issuer_name: str | None = None
	is_valid: bool
	revoked: bool
	revoked_at: str | datetime | None = None
	revoke_reason: str | None = None


class CertificateVerificationResponseModel(BaseModel):
	ok: bool
	certificate: CertificateVerificationModel


class BadgeTemplate(BaseModel):
	id: int
	created_at: str | datetime
	url: str
	template_name: str
	template_for: str | None = None
	event_name: str | None = None
	issuer_name: str | None = None
	notes: str | None = None


class Badge(BaseModel):
	id: int
	created_at: str | datetime
	template_id: int
	recipient_name: str
	recipient_email: str
	event_name: str | None = None
	event_date: str | None = None
	event_location: str | None = None
	issuer_name: str | None = None
	course_name: str | None = None
	issue_reason: str | None = None
	notes: str | None = None
	badge_id: str | None = None

class AddBadgeRequestModel(BaseModel):
    badge_id: str | None = None
    template_id: int
    recipient_name: str
    recipient_email: str
    event_name: str | None = None
    event_date: str | None = None
    event_location: str | None = None
    issuer_name: str | None = None
    course_name: str | None = None
    issue_reason: str | None = None
    notes: str | None = None
    

class AddBadgeTemplateRequestModel(BaseModel):
	template_name: str
	template_for: str | None = None
	event_name: str | None = None
	issuer_name: str | None = None
	notes: str | None = None	
