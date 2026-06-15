from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY

class _UnavailableTable:
    def __getattr__(self, name):
        def _raise(*args, **kwargs):
            raise RuntimeError("Supabase is not configured for this runtime")
        return _raise


class _UnavailableAuth:
    def __getattr__(self, name):
        def _raise(*args, **kwargs):
            raise RuntimeError("Supabase auth is not configured for this runtime")
        return _raise


class _UnavailableSupabase:
    auth = _UnavailableAuth()

    def table(self, *_args, **_kwargs):
        return _UnavailableTable()


if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    supabase = _UnavailableSupabase()
