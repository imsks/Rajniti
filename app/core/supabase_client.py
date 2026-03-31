from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

print("SUPABASE_URL:", SUPABASE_URL)
print("SUPABASE_KEY:", "SET" if SUPABASE_KEY else None)

if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("❌ Supabase ENV missing")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)