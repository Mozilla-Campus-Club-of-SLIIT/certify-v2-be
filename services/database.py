import logging
from datetime import datetime, timezone

from models.models import (
	AddCertificateRequestModel,
	AddTemplateRequestModel,
	RevokeCertificateRequestModel,
	AddBadgeRequestModel,
	AddBadgeTemplateRequestModel,
)
from services.supabase_client import get_supabase_client
from utils.certificate_id import generate_certificate_id
from utils.badge_id import generate_badge_id

audit_logger = logging.getLogger("certify.audit")


def add_template(url: str, request: AddTemplateRequestModel) -> dict:
	client = get_supabase_client()

	payload = {
		"url": url,
		"font_size": float(request.font_size),
		"font_color": request.font_color,
		"name_x_pos": request.name_x_pos,
		"name_y_pos": request.name_y_pos,
		"template_name": request.template_name,
		"template_for": request.template_for,
		"event_name": request.event_name,
		"issuer_name": request.issuer_name,
		"notes": request.notes,
	}

	response = client.table("templates").insert(payload).execute()
	if not response.data:
		raise ValueError("Failed to insert template record")

	return response.data[0]


def add_certificate(request: AddCertificateRequestModel) -> dict:
	client = get_supabase_client()
	certificate_id = request.certificate_id or generate_certificate_id()

	payload = {
		"certificate_id": certificate_id,
		"template_id": request.template_id,
		"recipient_name": request.recipient_name,
		"recipient_email": request.recipient_email,
		"issue_reason": request.issue_reason,
		"event_name": request.event_name,
		"event_date": request.event_date,
		"event_location": request.event_location,
		"issuer_name": request.issuer_name,
		"course_name": request.course_name,
		"notes": request.notes,
	}

	response = client.table("certificates").insert(payload).execute()
	if not response.data:
		raise ValueError("Failed to insert certificate record")

	return response.data[0]


def get_certificate_by_certificate_id(certificate_id: str) -> dict:
	client = get_supabase_client()
	response = (
		client.table("certificates")
		.select("*")
		.eq("certificate_id", certificate_id)
		.limit(1)
		.execute()
	)

	if not response.data:
		raise ValueError("Certificate not found")

	return response.data[0]


def get_template_by_id(template_id: int) -> dict:
	client = get_supabase_client()
	response = (
		client.table("templates")
		.select("*")
		.eq("id", template_id)
		.limit(1)
		.execute()
	)

	if not response.data:
		raise ValueError("Template not found")

	return response.data[0]


def revoke_certificate(certificate_id: str, request: RevokeCertificateRequestModel) -> dict:
	client = get_supabase_client()

	# Raises ValueError if the certificate doesn't exist, mirroring the 404 behavior
	# of the other lookups in this module.
	get_certificate_by_certificate_id(certificate_id)

	if request.revoked:
		payload = {
			"revoked": True,
			"revoked_at": datetime.now(timezone.utc).isoformat(),
			"revoked_by": request.revoked_by,
			"revoke_reason": request.reason,
		}
	else:
		payload = {
			"revoked": False,
			"revoked_at": None,
			"revoked_by": None,
			"revoke_reason": None,
		}

	response = (
		client.table("certificates")
		.update(payload)
		.eq("certificate_id", certificate_id)
		.execute()
	)

	if not response.data:
		raise ValueError("Failed to update certificate record")

	audit_logger.info(
		"certificate.revoke",
		extra={
			"certificate_id": certificate_id,
			"revoked": request.revoked,
			"revoked_by": request.revoked_by,
			"reason": request.reason,
		},
	)

	return response.data[0]


def get_all_templates() -> list[dict]:
	client = get_supabase_client()
	response = client.table("templates").select("id, template_name, created_at, issuer_name, event_name, notes, url").execute()

	if not response.data:
		return []

	return response.data

def get_all_badge_templates() -> list[dict]:
	client = get_supabase_client()
	response = client.table("badge_templates").select("id, created_at, url, template_name, template_for, event_name, issuer_name, notes").execute()

	if not response.data:
		return []

	return response.data


def get_all_certificates(template_id: int | None = None, recipient_email: str | None = None) -> list[dict]:
	client = get_supabase_client()
	query = client.table("certificates").select("id, certificate_id, created_at, template_id, recipient_name, recipient_email, issuer_name, revoked, revoked_at, revoked_by, revoke_reason")

	if template_id is not None:
		query = query.eq("template_id", template_id)

	if recipient_email is not None:
		query = query.eq("recipient_email", recipient_email)

	response = query.execute()

	if not response.data:
		return []

	return response.data

def get_badge_by_id(badge_id: str) -> dict:
  client = get_supabase_client()
  response = client.table("badges").select("id, created_at, template_id, recipient_name, recipient_email, event_name, event_date, event_location, issuer_name, course_name, issue_reason, notes, badge_id").eq("badge_id", badge_id).limit(1).execute()
  
  if not response.data:
    raise ValueError("Badge not found")
  
  badge = response.data[0]
  template_response = client.table("badge_templates").select("id, template_name, template_for, url").eq("id", badge["template_id"]).limit(1).execute()
  badge["badge_template"] = template_response.data[0] if template_response.data else None
  
  return badge

def add_badge_template(url: str, request: AddBadgeTemplateRequestModel) -> dict:
	client = get_supabase_client()

	payload = {
		"url": url,
		"template_name": request.template_name,
		"template_for": request.template_for,
		"event_name": request.event_name,
		"issuer_name": request.issuer_name,
		"notes": request.notes,
	}

	response = client.table("badge_templates").insert(payload).execute()
	if not response.data:
		raise ValueError("Failed to insert badge template record")

	return response.data[0]

def add_badge(request: AddBadgeRequestModel) -> dict:
	client = get_supabase_client()

	template_resp = (
		client.table("badge_templates")
		.select("id")
		.eq("id", request.template_id)
		.limit(1)
		.execute()
	)
	if not template_resp.data:
		raise ValueError(f"Badge template with id={request.template_id} not found")

	badge_id = request.badge_id or generate_badge_id()

	payload = {
		"badge_id":        badge_id,
		"template_id":     request.template_id,
		"recipient_name":  request.recipient_name,
		"recipient_email": request.recipient_email,
		"event_name":      request.event_name,
		"event_date":      request.event_date,
		"event_location":  request.event_location,
		"issuer_name":     request.issuer_name,
		"course_name":     request.course_name,
		"issue_reason":    request.issue_reason,
		"notes":           request.notes,
	}

	response = client.table("badges").insert(payload).execute()
	if not response.data:
		raise ValueError("Failed to insert badge record")

	return response.data[0]
	
def get_all_badges(
	template_id: int | None = None,
	recipient_name: str | None = None,
	issuer_name: str | None = None,
	limit: int = 50,
	offset: int = 0,
) -> list[dict]:
	client = get_supabase_client()

	query = client.table("badges").select(
		"id, created_at, badge_id, template_id, recipient_name, "
		"recipient_email, event_name, issuer_name, course_name, issue_reason"
	)

	if template_id is not None:
		query = query.eq("template_id", template_id)
	if recipient_name is not None:
		query = query.ilike("recipient_name", f"%{recipient_name}%")
	if issuer_name is not None:
		query = query.ilike("issuer_name", f"%{issuer_name}%")

	query = query.order("created_at", desc=True).range(offset, offset + limit - 1)

	response = query.execute()
	badges = response.data or []

	if not badges:
		return []

	template_ids = list({b["template_id"] for b in badges if b.get("template_id")})
	template_map: dict[int, str] = {}
	if template_ids:
		tmpl_resp = (
			client.table("badge_templates")
			.select("id, template_name")
			.in_("id", template_ids)
			.execute()
		)
		template_map = {t["id"]: t["template_name"] for t in (tmpl_resp.data or [])}

	for badge in badges:
		badge["badge_template_name"] = template_map.get(badge["template_id"])

	return badges
