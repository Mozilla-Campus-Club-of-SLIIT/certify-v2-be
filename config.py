from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "templates")
SUPABASE_BADGE_BUCKET = os.getenv("SUPABASE_BADGE_BUCKET", "badge-templates")

MAX_UPLOAD_SIZE = 50 * 1024 * 1024 #bytes
