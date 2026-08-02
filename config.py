from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "templates")

# Must match the JWT_SECRET configured on the accounts service
# (https://github.com/Mozilla-Campus-Club-of-SLIIT/accounts) so tokens it
# issues can be verified locally.
ACCOUNTS_JWT_SECRET = os.getenv("ACCOUNTS_JWT_SECRET", "")