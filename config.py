from dotenv import load_dotenv
import os

load_dotenv()

AUTH_API = os.getenv("AUTH_API", "https://accounts.sliitmozilla.org/api")
SUPABASE_URL =os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "templates")
SUPABASE_BADGE_BUCKET = os.getenv("SUPABASE_BADGE_BUCKET", "badge-templates")