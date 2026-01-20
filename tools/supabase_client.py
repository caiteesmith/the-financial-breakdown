from __future__ import annotations

import streamlit as st
from functools import lru_cache
from supabase import create_client, Client


@lru_cache(maxsize=1)
def get_supabase_client() -> Client:
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_ANON_KEY"]
    except KeyError:
        raise RuntimeError("Missing SUPABASE_URL or SUPABASE_ANON_KEY in Streamlit secrets.")

    return create_client(url, key)