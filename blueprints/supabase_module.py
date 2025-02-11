from supabase import create_client
from os import getenv
from dotenv import load_dotenv

load_dotenv()

supabase_url = getenv("SUPABASE_URL")
supabase_secret_key = getenv("SUPABASE_SECRET_KEY")

supabase_admin = create_client(supabase_url, supabase_secret_key)