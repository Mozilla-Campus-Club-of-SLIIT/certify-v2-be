# Certify v2 Backend

FastAPI backend for issuing and previewing certificates, backed by Supabase.

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and fill in the values (see below).
3. Run the API:
   ```
   uvicorn main:app --host 127.0.0.1 --port 8000 --reload
   ```

## Environment variables

| Variable          | Description                                              |
| ------------------ | --------------------------------------------------------- |
| `SUPABASE_URL`      | Supabase project URL                                       |
| `SUPABASE_KEY`      | Supabase service/API key                                   |
| `SUPABASE_BUCKET`   | Supabase storage bucket used for template uploads (default `templates`) |
| `ADMIN_API_KEY`     | Shared secret required to call the admin endpoints (see below) |

## Admin authentication

All routes under `/api/admin/*` (e.g. `POST /api/admin/add/template`, `POST /api/admin/add/certificate`) require a bearer token that matches the `ADMIN_API_KEY` environment variable.

Requests must include:

```
Authorization: Bearer <ADMIN_API_KEY>
```

- If the header is missing or the token doesn't match, the API responds `401 Unauthorized`.
- If `ADMIN_API_KEY` is not configured on the server, admin routes always respond `401 Unauthorized` (the API fails closed rather than allowing unauthenticated access).

Example:

```
curl -X POST https://<host>/api/admin/add/certificate \
  -H "Authorization: Bearer $ADMIN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{ "template_id": 1, "recipient_name": "Jane Doe", "recipient_email": "jane@example.com" }'
```

Generate a strong random value for `ADMIN_API_KEY` (e.g. `openssl rand -hex 32`) and keep it secret — anyone with this token can create templates and issue certificates.
