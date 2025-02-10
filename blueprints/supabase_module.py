from supabase import create_client
from os import getenv
from dotenv import load_dotenv

load_dotenv()

supabase_url = getenv("SUPABASE_URL")
supabase_anon_key = getenv("SUPABASE_ANON_KEY")
supabase_secret_key = getenv("SUPABASE_SECRET_KEY")

supabase_client = create_client(supabase_url, supabase_anon_key)
supabase_admin = create_client(supabase_url, supabase_secret_key)