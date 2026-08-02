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
| `ACCOUNTS_JWT_SECRET` | Must match the `JWT_SECRET` configured on the [accounts](https://github.com/Mozilla-Campus-Club-of-SLIIT/accounts) service — used to verify access tokens it issues (see below) |

## Admin authentication

All routes under `/api/admin/*` (e.g. `POST /api/admin/add/template`, `POST /api/admin/add/certificate`) require a valid access token issued by the [accounts](https://github.com/Mozilla-Campus-Club-of-SLIIT/accounts) SSO service, from a user whose token includes the `admin` role.

The accounts service issues HS256 JWTs whose claims include `id`, `name`, `email` and `roles` (an array of role names). This backend verifies that token locally — using the shared `ACCOUNTS_JWT_SECRET` — rather than calling back out to the accounts service, so `ACCOUNTS_JWT_SECRET` must be set to the exact same value as the accounts service's `JWT_SECRET`.

Requests must include:

```
Authorization: Bearer <access_token>
```

- If the header is missing, the token is invalid/expired, or `ACCOUNTS_JWT_SECRET` isn't configured, the API responds `401 Unauthorized`.
- If the token is valid but the user's `roles` claim doesn't include `admin`, the API responds `403 Forbidden`.

Example:

```
curl -X POST https://<host>/api/admin/add/certificate \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ "template_id": 1, "recipient_name": "Jane Doe", "recipient_email": "jane@example.com" }'
```

The role-checking middleware lives in [middleware/auth.py](middleware/auth.py) — `require_roles("admin")` can be reused on any router to gate it behind a specific role.
