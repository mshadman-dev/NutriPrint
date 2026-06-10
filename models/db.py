from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY

print("SUPABASE_URL =", SUPABASE_URL)
print("SUPABASE_KEY EXISTS =", bool(SUPABASE_KEY))

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
