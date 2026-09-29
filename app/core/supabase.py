# app/core/supabase.py
import os
from functools import lru_cache

from supabase import create_client, Client
# from app.core.config import settings


@lru_cache(maxsize=1)
def get_supabase() -> Client:
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    return create_client(SUPABASE_URL, SUPABASE_KEY)