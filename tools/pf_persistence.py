# =========================================
# file: tools/pf_persistence.py
# =========================================
from __future__ import annotations

from typing import Any, Dict, Optional

from tools.supabase_client import get_supabase_client


def load_pf_state(user_id: str) -> Optional[Dict[str, Any]]:
    supabase = get_supabase_client()
    res = (
        supabase.table("pf_state")
        .select("data")
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    if not res.data:
        return None
    return res.data[0].get("data")


def upsert_pf_state(user_id: str, data: Dict[str, Any]) -> None:
    supabase = get_supabase_client()
    supabase.table("pf_state").upsert(
        {"user_id": user_id, "data": data},
        on_conflict="user_id",
    ).execute()